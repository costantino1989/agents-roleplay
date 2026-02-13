from agents.base_agent import Agent
from config import MODEL_NAME
from prompts.hr_agent_prompt import HR_SYSTEM_PROMPT
from state import AgentState
from tools.schemas import rag_schema, save_employee_info_schema

# Initialize the HR Agent instance
hr_agent_instance = Agent(
    name="HR",
    system_prompt=HR_SYSTEM_PROMPT,
    model=MODEL_NAME,
    tools=[rag_schema, save_employee_info_schema],
    first_message="<system>Use the rag tool to generate the first question.</system>"
)


def hr_agent_node(state: AgentState):
    """
    Wrapper function to execute the HR Agent logic using the Agent class.
    Compatible with LangGraph node signature.
    """
    return hr_agent_instance.run(state)
