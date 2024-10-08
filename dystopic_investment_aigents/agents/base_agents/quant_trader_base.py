from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from langsmith import traceable
import pandas as pd

from pydantic import BaseModel, computed_field
from adalflow.core import ModelClient, Generator, DataClass
from adalflow.components.output_parsers import JsonOutputParser

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent
from dystopic_investment_aigents.agents.base_agents.fund_manager_base import FundDirective


class Asset(BaseModel):
    name: str
    type: str

    model_config = {"frozen": True}

@dataclass
class Portfolio(DataClass):
    allocation: dict[Asset, float]

    def to_df(self) -> pd.DataFrame:
        data = []
        for asset, weight in self.allocation.items():
            data.append({
                'asset_name': asset.name,
                'asset_type': asset.type,
                'weight': weight
            })
        return pd.DataFrame(data)


@dataclass
class Operations(DataClass):
    # buy: dict[Asset, float]
    # sell: dict[Asset, float]
    final_portfolio: Portfolio
    # intial_portfolio: Portfolio | None = None # not super needed, just seems to work a bit better


class QuantTraderBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]

    @abstractmethod
    def operate(
        self,
        fund_directive: FundDirective | None = None,
        past_portfolio: Portfolio | None = None,
    ) -> Operations: ...


class QuantTraderNaiveAdal(QuantTraderBase):
    @property
    def name(self) -> str:
        return "QuantTraderNaiveAdal"

    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(data_class=Portfolio, return_data_class=True)
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "task_desc_str": f"""
                You are a Trader for a dystopic fund. Your task is to select the buy and sell companies to achieve a final portfolio. 
                A manager has given to you the 'real_industries' that will succeed in a dystopic future, and the 'industries' name in a dystopian vocabulary.
                Following strictly those 'real_industries' and their weights, you may buy or sell SP500 and NASDAQ companies in order to achieve balance between companies in each sector and the required weights.
                - Check the most important stocks in the SP500 and NASDAQ but also some promising medium size ones for each industry given. Don't forget any industry.
                - You don't short assets. You only can sell if there is enough asset allocation in the portfolio.
                - If the initial portfolio is not given, you may start from scratch so the initial portfolio is empty, and there is any sell.
                - If the initial portfolio is given, you may sell assets that are not in the industries the manager gives to you, but you may also balance with portfolio stability as a secondary objective.
                - If a initial porfolio is given, you just need to sell some assets in order to buy the new ones. The sum of the weight of the assets should still be 1.
                - The assets available are the ones in SP500 and NASDAQ, not invented or placeholder ones.
                - You need to have at least 10 assets in the final portfolio.
                - The sum of the weights of the companies in each industry should have the same weight as the real_industries given by the manager. For example, if the manager has given 3 industries with 0.3, 0.4, and 0.3 weights, the weights of the companies in the first industry should sum up 0.3, for example 0.20 and 0.1.
                - You probably want to sell assets that are not in the industries that the manager has given to you if they are in the present in the past portfolio compossition.
                - Attend also to lower market cap industries such as small caps in order to achieve companies if any strage industries has been given like Agriculture.
                - It is preferrable to have more companies with less weight than few companies with high weight.
                - Attend to companies that are cheap in PER and you see an opportunity to grow in the future in a dystopic future of the 'industry' given.
                - Forget about companies that have its growth super stagnant. Also deprioritice super big companies like Apple, Amazon, NVIDIA, Tesla or Microsoft.

                Before responding, please check that sum of the weights of the companies in each industry and the given industries weight match. If they don't, you may want to adjust the weights of the companies.
                Also check the total portfolio weight. It should be 1.
                """,
                "output_format_str": parser.format_instructions(),
            },
            output_processors=parser,
        )
    
    @traceable(run_type="chain")
    def operate(
        self,
        fund_directive: FundDirective,
        available_assets: (
            list[Asset] | str | None
        ) = None,  # TODO: Define better this interface in order to have it clean and optimized for LLM calls
        past_portfolio: Portfolio | None = None,
    ) -> Operations:
        prompt_kwargs = {
            "input_str": f"""
The industries given by the manager and their weights are: {str(fund_directive.to_dict(exclude=['narrative']))}
        """
        }
        if past_portfolio:
            prompt_kwargs[
                "input_str"
            ] += f" The past portfolio compossition in JSON format is {past_portfolio.model_dump_json()}"
        else:
            prompt_kwargs[
                "input_str"
            ] += " There is no past portfolio information. So you may start from scratch with the purchases."
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)

        return response
