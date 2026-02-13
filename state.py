import operator
from typing import Annotated, List, TypedDict

from utils.llm_client import Message


class AgentState(TypedDict):
    """
    Represents the state of the HR Onboarding simulation.
    """
    messages: Annotated[List[Message], operator.add]
    hr_messages: Annotated[List[Message], operator.add]
    employee_messages: Annotated[List[Message], operator.add]
    name: str
    hr_name: str
    age: int
    country: str
    generation: str
    job_role: str
    sender: str
    language: str
