import os

import openai
from adalflow.components.model_client.openai_client import OpenAIClient
from langsmith.wrappers import wrap_openai


class OpenAIClientTraceable(OpenAIClient):  # type: ignore[misc]
    def init_sync_client(self) -> openai.OpenAI:
        api_key = self._api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Environment variable OPENAI_API_KEY must be set")
        return wrap_openai(openai.OpenAI(api_key=api_key))
