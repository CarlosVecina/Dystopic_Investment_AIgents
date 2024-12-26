from langsmith import traceable
from pydantic import computed_field
from adalflow.core import Generator
from adalflow.components.agent import ReActAgent
from dystopic_investment_aigents.agents.base_agents.analyst_base import AnalystBase
from dystopic_investment_aigents.agents.base_prompts.analyst_base_prompt import (
    ANALYST_AGENTS_SYSTEM_PROMPT,
)


class AnalystAdal(AnalystBase):
    @property
    def name(self) -> str:
        return "AnalystAdal"

    # https://lightrag.sylph.ai/tutorials/agent.html
    @computed_field()  # type: ignore[misc]
    @property
    def _react_brain(self) -> ReActAgent:
        return ReActAgent(
            max_steps=6,
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
        )

    @computed_field()  # type: ignore[misc]
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            template=ANALYST_AGENTS_SYSTEM_PROMPT,
            prompt_kwargs={
                "personality": f"I am {self.personality.mood.value} and I have a risk tolerance of {self.personality.risk_tolerance*100} %"
            },
        )

    @traceable(run_type="chain")
    def summarize(
        self, content: str, extra_instructions: list[str] | None = None
    ) -> str:
        prompt_kwargs = {"input_str": content}
        if extra_instructions:
            formatted_extra_instructions = ""
            for inst in extra_instructions:
                formatted_extra_instructions += "- " + inst + " \n"
            prompt_kwargs["extra_instructions"] = formatted_extra_instructions

        # self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)
        return response.data

    def generate_report(
        self, content: str, extra_instructions: list[str] | None = None
    ) -> str:  # Report:
        return self.summarize(content, extra_instructions)
