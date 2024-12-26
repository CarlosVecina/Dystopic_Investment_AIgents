from langsmith import traceable

from pydantic import computed_field
from adalflow.core import Generator
from adalflow.components.output_parsers import JsonOutputParser

from dystopic_investment_aigents.agents.base_agents.fund_manager_base import (
    FundDirective,
)
from dystopic_investment_aigents.agents.base_agents.quant_trader_base import (
    Asset,
    Operations,
    Portfolio,
    QuantTraderBase,
)
from dystopic_investment_aigents.agents.base_prompts.quant_trader_base_prompt import (
    QUANT_TRADER_AGENTS_SYSTEM_PROMPT,
)


class QuantTraderNaiveAdal(QuantTraderBase):
    @property
    def name(self) -> str:
        return "QuantTraderNaiveAdal"

    @computed_field()  # type: ignore[misc]
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(data_class=Operations, return_data_class=True)
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "personality": f"I am {self.personality.mood.value} and I have a risk tolerance of {self.personality.risk_tolerance*100} %",
            },
            template=QUANT_TRADER_AGENTS_SYSTEM_PROMPT,
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
            "input_str": (
                f"""
            The industries given by the manager and their weights are: {str(fund_directive.to_dict(exclude=['narrative']))}
            """
            )
        }
        if past_portfolio:
            prompt_kwargs["portfolio"] = past_portfolio.model_dump_json()

        # self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)

        return response
