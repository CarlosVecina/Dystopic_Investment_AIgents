from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from lightrag.components.output_parsers import JsonOutputParser
from lightrag.core import DataClass, Generator, ModelClient
from pydantic import computed_field

from dystopic_investment_aigents.agents.agent_base import Agent


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


class NewsletterAdal(NewsletterBase):
    @property
    def name(self) -> str:
        return "NewsletterAdal"

    @computed_field()
    @property
    def _generator_brain(self) -> Generator:
        # TODO: abstract the prompting and the Adal brain
        parser = JsonOutputParser(data_class=Newsletter, return_data_class=True)
        return Generator(
            model_client=self.seniority,
            model_kwargs=self.seniority_args,
            prompt_kwargs={
                "task_desc_str": f"""
You are a professional Newsletter creator that excell at narrative and catchy pieces.
Objective: Generate a high-quality weekly newsletter that includes updates, price movements, and portfolio operations.
Writing Guidelines:
- Tone and Style: Professional, informative, and engaging. Use a conversational tone to keep the reader interested.
- Language: Clear, concise, and free of jargon. Ensure complex terms are explained.
- Accuracy: Ensure all data and information are accurate and up-to-date.
- Visuals: Incorporate relevant visuals (charts, graphs, images) to enhance understanding.
- Length: Aim for a length of 1000-1500 words, ensuring content is comprehensive yet digestible.
- Utilize a {self.personality.mood.value} tone for the narrative.
- Add the disclaimer about informational purposes only and does not constitute financial advice. 

You will be provider with those last week inputs, and you should generate a newsletter with the main topics and the newsletter content.
                """,
                "output_format_str": parser.format_instructions(),
            },
            output_processors=parser,
        )

    def create_newsletter(self, context: str) -> Newsletter:
        prompt_kwargs = {"input_str": f"{context}"}

        self._generator_brain.print_prompt(**prompt_kwargs)
        response = self._generator_brain.call(prompt_kwargs=prompt_kwargs)

        return response
