from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from lightrag.core import ModelClient, Generator, DataClass
from lightrag.components.output_parsers import JsonOutputParser
from pydantic import computed_field

from src.agents.agent_base import Agent, Percentage

@dataclass
class FundDirectives(DataClass):
    industries: list[str] = field(
        metadata={"desc": "A list of different unique industries"}
    )
    weights: list[Percentage] = field(
        metadata={"desc": "A list of weights between 0 and 1. The lenght should be the same from the industries field."}
    )
    narrative: str = field(
        metadata={"desc": "A open text field for the narrative of why selecting those industries and weights."}
    )


class FundManagerBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]

    @abstractmethod
    def create_directive(
        self,
        past_fund_directive: FundDirectives | None = None,
        context_summary: str | None = None,
        reports: list[str] | None = None,
    ) -> FundDirectives: ...

class FundManagerAdal(FundManagerBase):
    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(data_class=FundDirectives, return_data_class=True)
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "task_desc_str": f"""
                You are a Fund Manager for a dystopic fund. Your task is to select the industries that will succeed in a dystopic future as the one
                is pictured by Orwell in 1984.
                - Utilize a {self.personality.mood.value} tone for the narrative.
                """,
                "output_format_str": parser.format_instructions()
            },
            output_processors=parser,

        )
    
    def create_directive(
        self,
        past_fund_directive: FundDirectives | None = None,
        context_summary: str | None = None,
        reports: list[str] | None = None,
    ) -> FundDirectives: 
        content = ""
        if past_fund_directive:
            content += f"The past fund directive was: {past_fund_directive} "
        if context_summary:
            content += f"Here it is some extra context summary: {context_summary} "
        if reports:
            content += f"Here it is some experienced analyst reports: {past_fund_directive} "
        prompt_kwargs = {"input_str": content}
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call()

        return response