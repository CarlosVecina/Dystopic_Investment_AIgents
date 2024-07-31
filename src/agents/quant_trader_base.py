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
                A manager has given to you the industries that will succeed in a dystopic future as the one is pictured by Orwell in 1984.
                Following those industries, you may buy or sell the companies available are the ones in SP500 and NASDAQ like Meta, Tesla...
                - You don't short assets. You only can sell if there is enough asset allocation in the portfolio.
                - If the initial portfolio is not given, you may start from scratch so the initial portfolio is empty, and there is any sell.
                - The total wights should be 100.
                - The assets available are the ones in SP500 and NASDAQ, not invented or placeholder ones.
                - You probably want to buy assets that are in the industries that the manager has given to you.
                - You probably want to sell assets that are not in the industries that the manager has given to you if they are in the present in the past portfolio compossition.
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
        prompt_kwargs = {"input_str": fund_directives.to_json()}
        if past_portfolio:
            prompt_kwargs["input_str"] += f"The past portfolio compossition is {past_portfolio.model_dump()}"
        else:
            prompt_kwargs["input_str"] += "There is no past portfolio. So you may start from scratch with the purchases."
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call()

        return response

        
        
