from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from adalflow.core import ModelClient, Generator, DataClass
from adalflow.components.output_parsers import JsonOutputParser
from langsmith import traceable
from pydantic import computed_field

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent, Percentage
from dystopic_investment_aigents.agents.base_agents.prompts.agent_prompt import FUND_MANAGER_AGENTS_SYSTEM_PROMPT


@dataclass
class FundDirective(DataClass):
    industries: list[str] = field(
        metadata={
            "desc": "A list of different unique industries with thematic names as the dystopic future."
        }
    )
    real_industries: list[str] = field(
        metadata={
            "desc": "The same list of industries, but each one should fit in current market industries like: 'Tech', 'Health', 'Finance', etc."
        }
    )
    weights: list[Percentage] = field(
        metadata={
            "desc": "A list of weights between 0 and 1. The lenght should be the same from the industries field."
        }
    )
    narrative: str = field(
        metadata={
            "desc": "A open text field for the narrative of why selecting those industries and weights."
        }
    )


class FundManagerBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]

    @abstractmethod
    def create_directive(
        self,
        past_fund_directive: FundDirective | None = None,
        context_summary: str | None = None,
        reports: list[str] | None = None,
    ) -> FundDirective: ...


class FundManagerAdal(FundManagerBase):
    @property
    def name(self) -> str:
        return "FundManagerAdal"

    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(
            data_class=FundDirective, return_data_class=True
        )
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            template=FUND_MANAGER_AGENTS_SYSTEM_PROMPT,
            prompt_kwargs={
                "personality": f"I am {self.personality.mood.value} and I have a risk tolerance of {self.personality.risk_tolerance*100} %",
                "output_format_str": parser.format_instructions(),
            },
            output_processors=parser,
        )

    @traceable(run_type="chain")
    def create_directive(
        self,
        past_fund_directive: FundDirective | None = None,
        context_summary: str | None = None,
        reports: list[str] | None = None,
    ) -> FundDirective:
        prompt_kwargs = {}
        if past_fund_directive:
            prompt_kwargs["past_fund_directives"] = past_fund_directive
        if context_summary:
            prompt_kwargs["extra_instructions"] = f"Here it is some extra context information summary: {context_summary} "
        if reports:
            prompt_kwargs["input_str"] = f"Here it is some experienced analyst reports: REPORT: {"\n \n REPORT: ".join(reports)}"
        
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)

        return response
