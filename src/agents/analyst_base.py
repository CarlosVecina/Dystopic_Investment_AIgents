from typing import Any
from pydantic import BaseModel, computed_field
from sqlalchemy import Connection
from lightrag.core import ModelClient, Generator
from lightrag.components.agent import ReActAgent
from abc import ABC, abstractmethod
from src.agents.agent_base import Agent


class Report(BaseModel):
    title: str
    content: str


class AnalystBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    seniority: ModelClient
    seniority_args: dict[str, Any]
    news_feed: Connection | None = None
    prices_feed: Connection | None = None

    @abstractmethod
    def summarize(self, content: str) -> str: ...

    @abstractmethod
    def generate_report(self, content: str) -> Report: ...


class AnalystAdal(AnalystBase):
    @computed_field()
    @property
    def _react_brain(self) -> ReActAgent:
        return ReActAgent(
            max_steps=6,
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
        )

    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "task_desc_str": f"""
                You are a helpful analyst. Your task is to summarize the following text in one or two sentences.
                Instructions:
                - Please, follow the input language for the output.
                - Do not add any information that is not present in the input.
                - Do not include your opinion or interpretation.
                - Utilize a {self.personality.value} tone.
                """
            },
        )

    def summarize(self, content: str) -> str:
        prompt_kwargs = {"input_str": content}
        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)
        return response.data
        # response = self._generator_brain.call(content)

    def generate_report(self, content: str) -> Report:
        return "Here it is my report"
