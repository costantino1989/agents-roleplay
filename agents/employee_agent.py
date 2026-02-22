from agents.base_agent import Agent
from config import MODEL_NAME
from prompts.francesca_prompt import FRANCESCA_SYSTEM_PROMPT
from prompts.luigi_prompt import LUIGI_SYSTEM_PROMPT
from state import AgentState

# Initialize the Employee Agent instance
employee_agent_instance = Agent(
    name="Employee",
    system_prompt="",
    model=MODEL_NAME,
    tools=None
)


def employee_agent_node(state: AgentState):
    """
    Wrapper function to execute the Employee Agent logic using the Agent class.
    Compatible with LangGraph node signature.
    """
    # Check if a specific prompt is provided in the state (dynamic profile)
    employee_prompt = state.get("employee_prompt")

    employee_agent_instance.system_prompt = employee_prompt
    employee_agent_instance._formatted_system_prompt = None

    return employee_agent_instance.run(state)
