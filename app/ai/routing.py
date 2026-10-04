from langchain_core.messages import AIMessage


def route_after_agent(state):
    """Determine routing after an agent step based on the latest AIMessage.

    This function is defensive: it safely accesses `tool_calls` and
    routes any requested tool to ToolNode, otherwise ends.
    """

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", None) or []
        if tool_calls:
            # tool_calls entries are dict-like with a 'name' key
            tool_name = tool_calls[0].get("name") if isinstance(tool_calls[0], dict) else None

            if tool_name:
                return "tools"

    return "end"
