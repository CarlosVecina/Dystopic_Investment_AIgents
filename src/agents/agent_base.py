from enum import Enum
from typing import Annotated, Any, Callable
from pydantic import BaseModel, Field


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
