from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, computed_field
from lightrag.core import ModelClient, Generator, DataClass
from lightrag.components.output_parsers import JsonOutputParser

from src.agents.agent_base import Agent
from src.agents.fund_manager_base import FundDirectives


class Asset(BaseModel):
    name: str
    type: str


class Portfolio(BaseModel):
    allocation: dict[Asset, float]

@dataclass
class Operations(DataClass):
    buy: dict[Asset, float]
    sell: dict[Asset, float]
    final_portfolio: Portfolio
    intial_portfolio: Portfolio | None = None


class QuantTraderBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]

    @abstractmethod
    def operate(
        self,
        fund_directives: FundDirectives | None = None,
        past_portfolio: Portfolio | None = None,
    ) -> Operations: ...

class QuantTraderNaiveAdal(QuantTraderBase):
    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(data_class=Operations, return_data_class=True)
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "task_desc_str": f"""
                You are a Trader for a dystopic fund. Your task is to select the buy and sell companies to achieve a final portfolio. 
                A manager has given to you the real_industries that will succeed in a dystopic future.
                Following strictly those real_industries and their weights, you may buy or sell SP500 and NASDAQ companies in order to achieve companies in each sector in the required weights.
                - Check the most important stocks in the SP500 and NASDAQ and also some promising medium size ones for each industry given.
                - You don't short assets. You only can sell if there is enough asset allocation in the portfolio.
                - If the initial portfolio is not given, you may start from scratch so the initial portfolio is empty, and there is any sell.
                - The total wights should be 100.
                - The assets available are the ones in SP500 and NASDAQ, not invented or placeholder ones.
                - You need to have at least 10 assets in the final portfolio.
                - The companies in the industry should have the same weight as the real_industries given by the manager. For example, if the manager has given 3 industries with 0.3, 0.4, and 0.3 weights, the weights of the companies in the first industry should sum up 0.3, for example 0.20 and 0.1.
                - You probably want to sell assets that are not in the industries that the manager has given to you if they are in the present in the past portfolio compossition.
                - Attend also to lower market cap industries such as small caps in order to achieve companies if any strage industries has been given like Agriculture.
                - It is preferrable to have more companies with less weight than few companies with high weight.
                - Attend to companies that are cheap in PER and you see an opportunity to grow in the future.

                Before responding, please check that sum of the weights of the companies in each industry and the given industries weight match. If they don't, you may want to adjust the weights of the companies.
                """,
                "output_format_str": parser.format_instructions()
            },
            output_processors=parser,

        )
    
    def operate(
        self,
        available_assets: list[Asset] | str, #TODO: Define better this interface in order to have it clean and optimized for LLM calls
        fund_directives: FundDirectives,
        past_portfolio: Portfolio | None = None,
    ) -> Operations: 
        prompt_kwargs = {
            "input_str": f"""
The industries given by the manager and their weights are: {str(fund_directives.to_dict(exclude=['industries', 'narrative']))}
        """}
        if past_portfolio:
            prompt_kwargs["input_str"] += f" The past portfolio compossition is {past_portfolio.model_dump()}"
        else:
            prompt_kwargs["input_str"] += " There is no past portfolio information. So you may start from scratch with the purchases."
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call()

        return response

        
        
