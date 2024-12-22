from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from adalflow import DataClass

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent, Percentage


@dataclass
class FundDirective(DataClass):
    industries: list[str] = field(
        metadata={
            "description": "A list of different unique industries with thematic names as the dystopic future."
        }
    )
    real_industries: list[str] = field(
        metadata={
            "description": "The same list of industries, but each one should fit in current market industries like: 'Tech', 'Health', 'Finance', etc."
        }
    )
    weights: list[Percentage] = field(
        metadata={
            "description": "A list of weights between 0 and 1. The length should be the same as the industries field."
        }
    )
    narrative: str = field(
        metadata={
            "description": "An open text field for the narrative of why selecting those industries and weights."
        }
    )


class FundManagerBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    @abstractmethod
    def create_directive(
        self,
        past_fund_directive: FundDirective | None = None,
        context_summary: str | None = None,
        reports: list[str] | None = None,
    ) -> str: ...  # FundDirective: ...
