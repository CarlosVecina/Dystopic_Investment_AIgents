from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import Connection

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent


class Report(BaseModel):
    title: str
    content: str


class AnalystBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    news_feed: Connection | None = None
    prices_feed: Connection | None = None

    @abstractmethod
    def summarize(self, content: str) -> str: ...

    @abstractmethod
    def generate_report(
        self, content: str, extra_instructions: list[str] | None = None
    ) -> str: ...
