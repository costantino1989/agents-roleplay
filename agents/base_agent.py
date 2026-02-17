import concurrent.futures
import opik
import time
from state import AgentState
from typing import Any, Dict, List, Optional
from utils.llm_client import LLMClient, Message
from utils.logger import get_logger


class Agent:
    def __init__(
            self,
            name: str,
            system_prompt: str,
            model: str,
            tools: Optional[List[Dict[str, Any]]] = None,
            first_message: Optional[str] = None
    ):
        """
        Initialize a generic Agent.

        Args:
            name (str): The name of the agent (e.g., "HR", "Employee").
            system_prompt (str): The template string for the system prompt.
            model (str): The model name to use.
            tools (Optional[List[Dict]]): List of tool schemas.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.client = LLMClient(model=model)
        self.logger = get_logger(f"{name}Agent")
        self.first_message = first_message
        self._formatted_system_prompt = None
        self.executor = concurrent.futures.ThreadPoolExecutor()

    @opik.track
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Executes the agent logic: formats prompt, calls LLM, logs time, returns state update.
        """
        self.logger.debug(f"--- {self.name} Thinking ---")
        start_time = time.perf_counter()

        # 1. Format System Prompt
        system_msg = self._get_formatted_system_message(state)

        # 2. Prepare Messages history
        messages, last_other_msg = self._prepare_messages(state, system_msg)

        # 3. Call LLM
        response_msg = self.client.chat(messages, tools=self.tools)

        # 5. Log Execution Time
        end_time = time.perf_counter()
        duration = end_time - start_time
        self.logger.info(f"Execution time: {duration:.4f}s")

        # 6. Return State Update
        return self._create_state_update(response_msg, last_other_msg)

    def _get_formatted_system_message(self, state: AgentState) -> Message:
        if self._formatted_system_prompt is None:
            try:
                self._formatted_system_prompt = self.system_prompt.format(**state)
            except KeyError as e:
                self.logger.error(f"Missing key in state for prompt formatting: {e}")
                raise e
            except Exception as e:
                self.logger.error(f"Error formatting prompt: {e}")
                raise e
        return Message(role="system", content=self._formatted_system_prompt)

    def _prepare_messages(self, state: AgentState, system_msg: Message) -> tuple[List[Message], Optional[Message]]:
        # TODO Needs do agnostic selection of history based on sender
        current_history: List[Message] = state.get("hr_messages" if self.name == "HR" else "employee_messages", [])
        other_history: List[Message] = state.get("employee_messages" if self.name == "HR" else "hr_messages", [])
        first_message = [Message(role="user", content=self.first_message)] if self.first_message else []
        messages = [system_msg] + first_message + current_history

        last_other_msg = None

        # If the last sender was the other agent, we "absorb" their last message into our context as 'user'
        if other_history and (other_content := other_history[-1].content):
            last_other_msg = Message(role="user", content=other_content)
            messages.append(last_other_msg)

        return messages, last_other_msg

    def _create_state_update(self, response_msg: Message, last_other_msg: Optional[Message]) -> Dict[str, Any]:
        update = {
            "messages": [response_msg],
            "sender": self.name.lower()
        }
        # Prepare the incremental update for the agent-specific history
        agent_list_update = []
        if last_other_msg:
            agent_list_update.append(last_other_msg)
        agent_list_update.append(response_msg)
        if self.name == "HR":
            update["hr_messages"] = agent_list_update
        else:
            update["employee_messages"] = agent_list_update

        return update
