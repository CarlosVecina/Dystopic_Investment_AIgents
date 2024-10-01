import os
from datetime import datetime

import pandas as pd
from adalflow import OpenAIClient
from openai import BaseModel
from sqlalchemy import Engine, create_engine, text

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent
from dystopic_investment_aigents.agents.base_agents.analyst_base import (
    AnalystAdal,
    AnalystBase,
)
from dystopic_investment_aigents.agents.base_agents.fund_manager_base import (
    FundDirective,
    FundManagerAdal,
    FundManagerBase,
)
from dystopic_investment_aigents.agents.base_agents.quant_trader_base import (
    Portfolio,
    QuantTraderBase,
    QuantTraderNaiveAdal,
)
from dystopic_investment_aigents.data_ingestion.db.postgres_db import PostgresConfig

NEWS_TABLE = "news_yh"
NEWS_TABLE_DATE_COL = "created_at"
NEWS_TABLE_CONTENT_COL = "related_tickers"


class Fund(BaseModel):
    name: str
    description: str
    manager: FundManagerBase
    analyst: list[AnalystBase]
    trader: QuantTraderBase
    possible_assets: list[str]
    engine: Engine
    portfolio: Portfolio | None = None

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

    def run(self) -> None:
        # 1. Analysts analyze the market
        df_news = self._get_lastest_news(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 8, 31),
            related_ids=["AAPL"],
        )
        # Filter out null values and extract 'body' column content
        news_content = df_news['body'].dropna().to_string(index=False)

        list_analysis = []
        for analyst in self.analyst:
            list_analysis.append(analyst.generate_report(news_content))
        
        # 2. Analysts provide fund manager with analysis
        last_directive = self._get_last_directive()
        directive = self.manager.create_directive(past_fund_directive=last_directive, reports=list_analysis)
        
        # 3. Trader executes portfolio
        last_portfolio = self._get_last_portfolio()
        breakpoint()
        opeerations = self.trader.operate(fund_directive=directive, past_portfolio=last_portfolio)
        print(opeerations)

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    the_boss = FundManagerAdal(
        personality={"mood": "optimistic", "risk_tolerance": 0.5},
        seniority=OpenAIClient(),
        seniority_args={
            "model": "gpt-4o-mini",
            "temperature": 0.0,
        },
    )
    the_analyst01 = AnalystAdal(
        personality={"mood": "optimistic", "risk_tolerance": 0.5},
        seniority=OpenAIClient(),
        seniority_args={
            "model": "gpt-4o-mini",
            "temperature": 0.0,
        },
    )
    the_trader01 = QuantTraderNaiveAdal(
        personality={"mood": "optimistic", "risk_tolerance": 0.5},
        seniority=OpenAIClient(),
        seniority_args={
            "model": "gpt-4o-mini",
            "temperature": 0.9,
        },
    )

    db_uri = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"],
    ).get_connection_string()

    engine = create_engine(db_uri)

    fund = Fund(
        name="Dystopic Fund",
        description="A fund that invests in the future",
        manager=the_boss,
        analyst=[the_analyst01],
        trader=the_trader01,
        possible_assets=["stocks"],
        engine=engine,
    )
    fund.run()
