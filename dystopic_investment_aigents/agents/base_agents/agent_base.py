from enum import Enum
from typing import Annotated, Any, Callable

from pydantic import BaseModel, Field
from openai.types.chat.chat_completion import ChatCompletion

from dystopic_investment_aigents.agents.base_agents.memory_base import (
    ConversationMemory,
)
from dystopic_investment_aigents.utils.model_client_utils import OpenAIClientTraceable


class Mood(Enum):
    OPTIMISTIC = "optimistic"
    PESIMISTIC = "pesimistic"
    DYSTOPIC = "dystopic"


Percentage = Annotated[float, Field(gt=0, lt=1)]


class Personality(BaseModel):
    mood: Mood
    risk_tolerance: Percentage


class Agent(BaseModel):
    personality: Personality
    toolset: list[Callable[[Any], Any]] | None = None
    seniority: OpenAIClientTraceable
    seniority_args: dict[str, Any]
    memory: ConversationMemory

    model_config = {"arbitrary_types_allowed": True}

    def discuss(self, message: str) -> str:
        response: ChatCompletion = self.seniority.sync_client.chat.completions.create(
            messages=[{"role": "user", "content": message}], **self.seniority_args
        )
        response_text = response.choices[0].message.content
        self.memory.add_message(response_text, "assistant")
        return response_text
