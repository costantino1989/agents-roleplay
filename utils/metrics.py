# from opik.evaluation.models import LiteLLMChatModel
# EVAL_MODEL = LiteLLMChatModel(
#     model_name=EVAL_MODEL_NAME,
#     base_url=EVAL_BASE_URL,
#     api_key=EVAL_API_KEY
# )
from config import EVAL_API_KEY, EVAL_BASE_URL, EVAL_MODEL_NAME
from openai import OpenAI
from opik.evaluation.metrics import AnswerRelevance, Hallucination
from opik.evaluation.models import OpikBaseModel
from typing import Any


class CustomOpenAICompatibleModel(OpikBaseModel):
    def __init__(self, model_name: str, api_key: str, base_url: str):
        super().__init__(model_name)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def generate_string(self, input: str, **kwargs: Any) -> str:
        """
        This method is used as part of LLM as a Judge metrics to take a string prompt, pass it to
        the model as a user message and return the model's response as a string.
        """
        conversation = [
            {
                "content": input,
                "role": "user",
            },
        ]

        provider_response = self.generate_provider_response(messages=conversation, **kwargs)
        return provider_response.choices[0].message.content

    def generate_provider_response(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        """
        This method is used as part of LLM as a Judge metrics to take a list of AI messages, pass it to
        the model and return the full model response.
        """
        response = self.client.chat.completions.parse(
            model=self.model_name,
            messages=messages,
            **kwargs
        )
        return response


EVAL_MODEL = CustomOpenAICompatibleModel(
    model_name=EVAL_MODEL_NAME,
    base_url=EVAL_BASE_URL,
    api_key=EVAL_API_KEY
)

answer_relevance_metric = AnswerRelevance(model=EVAL_MODEL, require_context=False)
