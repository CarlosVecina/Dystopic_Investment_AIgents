from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel


class Personality(Enum):
    OPTIMISTIC = "optimistic"
    PESIMISTIC = "pesimistic"
    DYSTOPIC = "dystopic"


class Agent(BaseModel):
    personality: Personality
    toolset: list[Callable[[Any], Any]] | None = None
