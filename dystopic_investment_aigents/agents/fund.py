import os
import pathlib
from datetime import datetime
from typing import Literal
import logging

from dotenv import load_dotenv

import pandas as pd
from adalflow import GeneratorOutput
from langsmith import traceable
from openai import BaseModel
from sqlalchemy import Engine, text

from dystopic_investment_aigents.agents.base_agents.fund_manager_base import (
    FundDirective,
)
from dystopic_investment_aigents.agents.discussion import Discussion
from dystopic_investment_aigents.agents.impl_agents.fund_manager_adal import (
    FundManagerAdal,
)
from dystopic_investment_aigents.agents.base_agents.quant_trader_base import (
    Operations,
    Portfolio,
)
from dystopic_investment_aigents.agents.impl_agents.quant_trader_adal import (
    QuantTraderNaiveAdal,
)
from dystopic_investment_aigents.agents.impl_agents.analyst_adal import AnalystAdal
from dystopic_investment_aigents.knowledge_base.db import supabase_engine
from dystopic_investment_aigents.utils.yaml_utils import YAMLUtils

NEWS_TABLE = "news_yh"
NEWS_TABLE_DATE_COL = "created_at"
NEWS_TABLE_CONTENT_COL = "related_tickers"

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

load_dotenv()


class Fund(BaseModel):
    name: str
    description: str
    type: Literal["rag", "discussion"]
    manager: FundManagerAdal
    analyst: AnalystAdal | list[AnalystAdal]
    trader: QuantTraderNaiveAdal
    possible_assets: list[str]
    engine: Engine
    portfolio: Portfolio | None = None

    dry_run: bool = True

    model_config = {"arbitrary_types_allowed": True}

    # TODO: move to database class
    def _get_lastest_news(
        self,
        start_date: datetime,
        end_date: datetime,
        related_ids: list[str] | None = None,
    ) -> pd.DataFrame:
        query = f"""
            SELECT * FROM {NEWS_TABLE}
            WHERE {NEWS_TABLE_DATE_COL} BETWEEN '{start_date}' AND '{end_date}'
        """

        if related_ids:
            related_ids_clause = " OR ".join(
                [f"{NEWS_TABLE_CONTENT_COL} ILIKE '%{id}%'" for id in related_ids]
            )
            query += f" AND ({related_ids_clause})"

        query += f" ORDER BY {NEWS_TABLE_DATE_COL} DESC"

        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            column_names = result.keys()
            results = result.fetchall()
        return pd.DataFrame(results, columns=column_names)

    def _get_last_directive(self) -> FundDirective | None:
        return None

    def _get_last_portfolio(self) -> Portfolio | None:
        return None

    def _persist_directive(self, directive: FundDirective) -> None:
        from sqlalchemy import Column, DateTime, Float, MetaData, String, Table
        from sqlalchemy.dialects.postgresql import ARRAY

        # Create or get the fund_directive table
        metadata = MetaData()
        fund_directive_table = Table(
            "fund_directives",
            metadata,
            Column("industries", ARRAY(String)),
            Column("real_industries", ARRAY(String)),
            Column("weights", ARRAY(Float)),
            Column("narrative", String),
            Column("created_at", DateTime),
        )

        # Create the table if it doesn't exist
        metadata.create_all(self.engine)

        # Prepare the data to be inserted
        current_time = datetime.now()

        data_to_insert = {
            "industries": directive.industries,
            "real_industries": directive.real_industries,
            "weights": directive.weights,
            "narrative": directive.narrative,
            "created_at": current_time,
        }

        # Insert the data
        with self.engine.connect() as connection:
            connection.execute(fund_directive_table.insert().values(data_to_insert))
            connection.commit()

    def _persist_final_portfolio(self, operations: dict[str, float]) -> None:
        from sqlalchemy import Column, DateTime, Float, MetaData, String, Table

        # Create or get the portfolio table
        metadata = MetaData()
        portfolio_table = Table(
            "portfolio",
            metadata,
            Column("asset_name", String(255)),
            Column("weight", Float),
            Column("asset_short_name", String(255)),
            Column("asset_type", String(255)),
            Column("portfolio_trader", String(255)),
            Column("created_at", DateTime),
        )

        # Create the table if it doesn't exist
        metadata.create_all(self.engine)

        # Prepare the data to be inserted
        current_time = datetime.now()

        parent_dir = pathlib.Path(__file__).parent.parent
        symbol_mapping = pd.read_csv(
            os.path.join(parent_dir, "utils", "symbol_mapping.csv"), sep=";"
        )[["Company", "Symbol"]]

        data_to_insert = [
            {
                "asset_name": k,
                "weight": v,
                "asset_short_name": next(
                    iter(
                        symbol_mapping.loc[
                            symbol_mapping["Company"]
                            .str.lower()
                            .str.contains(k.lower()),
                            "Symbol",
                        ].values
                    ),
                    None,
                ),
                "asset_type": "stock",
                "portfolio_trader": self.trader.__class__.__name__,
                "created_at": current_time,
            }
            for k, v in operations.items()
        ]

        # Insert the data into the database
        with self.engine.connect() as connection:
            connection.execute(portfolio_table.insert().values(data_to_insert))
            connection.commit()

        logger.info(f"Final portfolio persisted with {len(data_to_insert)} operations.")

    @traceable
    def run(self) -> None:
        # 1. Analysts analyze the market
        logger.info("Starting market analysis...")
        df_news = self._get_lastest_news(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 8, 31),
            related_ids=["AAPL"],
        )
        logger.info(f"Retrieved {len(df_news)} news articles")

        # Filter out null values and extract 'body' column content
        news_content = df_news["body"].dropna().to_string(index=False)
        logger.debug("Processed news content")

        if isinstance(self.analyst, AnalystAdal):
            self.analyst = [self.analyst]

        logger.info("Generating analyst reports...")
        list_analysis = []
        for i, analyst in enumerate(self.analyst):
            logger.debug(f"Analyst {i+1}/{len(self.analyst)} generating report...")
            list_analysis.append(analyst.generate_report(news_content))
        logger.info(f"Generated {len(list_analysis)} analyst reports")

        # 2. Analysts provide fund manager with analysis
        logger.info("Getting last directive...")
        last_directive = self._get_last_directive()

        # TODO: tidy up fund execution
        if self.type == "discussion":
            logger.info("Starting discussion between analysts and fund manager...")
            discussion = Discussion(
                topic=f"Clarify the fund's strategy. Remember that the fund {self.description}",
                max_turns=3,
                participants=[
                    (
                        self.manager,
                        f"Clarify the fund's strategy. Inquisitive questions to analysts. The last directive is: {last_directive}",
                    )
                ]
                + [
                    (
                        analyst,
                        f"Defend your analysis but be open to questions. Your analysis is: {list_analysis[i]}",
                    )
                    for i, analyst in enumerate(self.analyst)
                ],
            )()
            logger.info("Discussion completed")
            directive = self.manager.create_directive(
                past_fund_directive=last_directive,
                reports=list_analysis,
                context_summary=f"This is a discussion you had with the analysts {discussion}",
            )
            breakpoint()
        else:
            logger.info("Creating fund directive without discussion...")
            directive = self.manager.create_directive(
                past_fund_directive=last_directive, reports=list_analysis
            )
        logger.info("Persisting new directive...")
        self._persist_directive(directive)

        # 3. Trader executes portfolio
        logger.info("Getting last portfolio state...")
        last_portfolio = self._get_last_portfolio()
        logger.info("Executing trading operations...")
        operations: GeneratorOutput[Operations] = self.trader.operate(
            fund_directive=directive, past_portfolio=last_portfolio
        )
        if not self.dry_run:
            try:
                logger.info("Persisting final portfolio...")
                self._persist_final_portfolio(
                    operations.data.final_portfolio.allocation
                )
                logger.info("Portfolio successfully persisted")
            except Exception as e:
                logger.error(f"Error persisting final portfolio: {e}")

        return operations


if __name__ == "__main__":
    with open("config/fund_config.yaml", "r") as file:
        config = YAMLUtils.safe_load(file)

    config["possible_assets"] = ["stocks"]
    config["engine"] = supabase_engine

    fund = Fund.model_validate(config)
    fund.run()
