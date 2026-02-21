import inspect
import opik
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from opik import opik_context
from typing import Any, Dict, List, Optional

load_dotenv()


@dataclass
class Message:
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Any]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content

        if self.tool_calls is not None:
            # Handle list of tool calls which might be Pydantic models or dicts
            serialized_tool_calls = []
            for tc in self.tool_calls:
                if hasattr(tc, 'model_dump'):
                    serialized_tool_calls.append(tc.model_dump())
                elif hasattr(tc, 'dict'):
                    serialized_tool_calls.append(tc.dict())
                else:
                    serialized_tool_calls.append(tc)
            data["tool_calls"] = serialized_tool_calls

        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            data["name"] = self.name
        return data


class LLMClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = OpenAI(
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = model

    @opik.track
    def chat(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> Message:
        """
        Sends a chat completion request to the LLM.
        """
        openai_messages = [msg.to_dict() for msg in messages]

        params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": 0.8,
            "top_p": 0.98,
            "presence_penalty": 0.7,
            "frequency_penalty": 0.5,
            "extra_body": {
            }
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
            params["parallel_tool_calls"] = True

        response = self.client.chat.completions.create(**params)

        # Opik tracking: Manually set provider and model name for cost tracking
        if response.usage:
            usage_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            # Update the current span with usage and model info
            opik_context.update_current_span(
                model=self.model,
                usage=usage_data
            )

        choice = response.choices[0]
        message_obj = choice.message

        message = Message(
            role=message_obj.role,
            content=message_obj.content,
            tool_calls=message_obj.tool_calls
        )

        return message


def function_to_schema(func) -> Dict[str, Any]:
    """
    Converts a Python function to an OpenAI tool schema.
    Simple implementation relying on docstrings and type hints.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }

    signature = inspect.signature(func)
    parameters = {}
    required = []

    for name, param in signature.parameters.items():
        param_type = type_map.get(param.annotation, "string")
        parameters[name] = {
            "type": param_type,
            "description": f"Parameter {name}"
        }
        if param.default == inspect.Parameter.empty:
            required.append(name)

    # basic docstring parsing
    description = func.__doc__.strip() if func.__doc__ else "No description"

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
    }
