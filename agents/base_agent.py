import concurrent.futures
import opik
import time
from opik import opik_context
from state import AgentState
from typing import Any, Dict, List, Optional
from utils.llm_client import LLMClient, Message
from utils.logger import get_logger
from utils.metrics import answer_relevance_metric


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

        # Capture trace ID from the main thread context
        trace_data = opik_context.get_current_trace_data()
        trace_id = trace_data.id if trace_data else None

        self.logger.debug(f"trace_id: {trace_id}")

        # 4. Calculate Metrics (Async/Parallel)
        self._calculate_metrics(messages, response_msg, trace_id)

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

    def _calculate_metrics(self, messages: List[Message], response_msg: Message, trace_id: str) -> None:
        try:
            # Determine Input (last user message)
            input_text = ""
            for msg in reversed(messages):
                if msg.role == "user":
                    input_text = msg.content
                    break

            def calc_relevance(trace_id):
                if response_msg.content and input_text and trace_id:
                    try:
                        score_result = answer_relevance_metric.score(
                            input=input_text,
                            output=response_msg.content
                        )
                        client = opik.Opik(project_name="agents-roleplay")
                        client.log_traces_feedback_scores(
                            scores=[{"id": trace_id, "name": "Answer Relevance", "value": score_result.value}],
                            project_name="agents-roleplay"
                        )
                    except Exception as e:
                        self.logger.warning(f"Error calculating Answer Relevance: {e}")

            # Fire and forget tasks
            if trace_id:
                self.executor.submit(calc_relevance, trace_id)
            else:
                self.logger.warning("No active Opik trace found, metrics will not be logged.")

        except Exception as e:
            self.logger.warning(f"Failed to initiate Opik metrics: {e}")

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

    def shutdown(self):
        """
        Gracefully shuts down the thread pool executor, waiting for pending tasks to complete.
        """
        self.logger.info(f"Shutting down {self.name}Agent executor...")
        self.executor.shutdown(wait=True)
        self.logger.info(f"{self.name}Agent executor shut down.")
