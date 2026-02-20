from typing import Any

from openai import OpenAI
from opik.evaluation.models import OpikBaseModel


class CustomOpenAICompatibleModel(OpikBaseModel):
    def __init__(self, model_name: str, api_key: str, base_url: str):
        super().__init__(model_name)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,  # e.g., "https://openrouter.ai/api/v1"
        )

    def generate_string(self, input: str, **kwargs: Any) -> str:
        """
        Used by LLM-as-a-Judge metrics: takes a string prompt, passes it to
        the model as a user message and returns the model's response as a string.
        """
        conversation = [{"role": "user", "content": input}]
        provider_response = self.generate_provider_response(messages=conversation, **kwargs)
        return provider_response.choices[0].message.content

    def generate_provider_response(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        """
        Used by LLM-as-a-Judge metrics: takes a list of messages, passes them to
        the model and returns the full ChatCompletion response object.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )