from state import AgentState
from typing import Literal


def should_continue(state: AgentState) -> Literal["tools", "employee", "end"]:
    messages = state["messages"]
    last_message = messages[-1]

    # If HR called a tool
    if last_message.tool_calls:
        return "tools"

    # If it's HR's turn output (text), check if they said goodbye
    if state["sender"] == "hr":
        text = last_message.content.strip().lower() if last_message.content else ""
        if text.endswith("goodbye"):
            # Pass to employee for one last goodbye
            return "employee"
        return "employee"

    # If it's Employee's turn output
    if state["sender"] == "employee":
        # Check if this was a goodbye response
        text = last_message.content.strip().lower() if last_message.content else ""
        if "grazie e arrivederci" in text:
            return "end"
        return "hr"

    return "end"
