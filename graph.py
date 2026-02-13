import json
from langgraph.graph import END, START, StateGraph

from agents.employee_agent import employee_agent_node
from agents.hr_agent import hr_agent_node
from agents.utils import should_continue
from state import AgentState
from tools.profile_tool import save_employee_info
from tools.rag_tool import rag
from utils.llm_client import Message
from utils.logger import get_logger
from vector_db.client import GenzeloVectorDB

logger = get_logger("Graph")


def build_graph(db_client: GenzeloVectorDB):
    
    def tools_node(state: AgentState):
        """
        Executes tools requested by the HR agent.
        """
        logger.debug("--- Executing Tools ---")
        messages = state["messages"]
        last_message = messages[-1]

        tool_results = []

        if last_message.tool_calls:
            # TODO Tools should be called in parallel
            for tool_call in last_message.tool_calls:
                # OpenAI object, not dict
                # tool_call has id, type, function
                # function has name, arguments (str)

                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id

                result = f"Error: Tool {function_name} not found."

                if function_name == "rag":
                    result = rag(client=db_client, **arguments)
                elif function_name == "save_employee_info":
                    # Inject employee name from state to personalize the file
                    employee_name = state.get("name")
                    result = save_employee_info(employee_name=employee_name, **arguments)

                # Create Tool Message
                tool_msg = Message(
                    role="tool",
                    content=str(result),
                    tool_call_id=tool_call_id,
                    name=function_name
                )
                tool_results.append(tool_msg)

        return {"messages": tool_results, "hr_messages": tool_results}

    workflow = StateGraph(AgentState)

    workflow.add_node("hr", hr_agent_node)
    workflow.add_node("employee", employee_agent_node)
    workflow.add_node("tools", tools_node)

    # Start with HR
    workflow.add_edge(START, "hr")

    # HR -> Tools or Employee
    workflow.add_conditional_edges(
        "hr",
        should_continue,
        {
            "tools": "tools",
            "employee": "employee",
            "end": END
        }
    )

    # Tools -> HR
    workflow.add_edge("tools", "hr")

    # Employee -> HR or End
    workflow.add_conditional_edges(
        "employee",
        should_continue,
        {
            "hr": "hr",
            "end": END
        }
    )

    return workflow.compile()
