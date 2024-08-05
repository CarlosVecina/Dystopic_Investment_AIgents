from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from lightrag.core import ModelClient, DataClass

from src.agents.agent_base import Agent


@dataclass
class Newsletter(DataClass):
    title: str
    main_topics: str
    newsletter: str


class NewsletterBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]

    @abstractmethod
    def create_newsletter(
        self, context: str  # TODO: define the inputs for the newsletter
    ) -> Newsletter: ...
