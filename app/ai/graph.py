from langgraph.graph import (
    StateGraph,
    MessagesState,
    START,
    END,
)

from langgraph.prebuilt import ToolNode

from app.ai.nodes.agent import agent_node

from app.tools.shipment_tools import get_shipment_status
from app.tools.rag_tools import search_internal_knowledge
from app.ai.routing import route_after_agent


def build_graph():

    graph = StateGraph(MessagesState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    graph.add_node("agent", agent_node)

    graph.add_node(
        "tools",
        ToolNode(
            [
                get_shipment_status,
                search_internal_knowledge,
            ]
        ),
    )

    # --------------------------------------------------
    # Entry
    # --------------------------------------------------

    graph.add_edge(
        START,
        "agent",
    )

    # --------------------------------------------------
    # Agent routing
    # --------------------------------------------------

    graph.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "shipment_tool": "tools",
            "rag": "tools",
            "end": END,
        },
    )

    # --------------------------------------------------
    # Tool routing
    # --------------------------------------------------

    # After a tool executes, return control to the agent so it can
    # compose a natural-language response using the tool result.
    graph.add_edge(
        "tools",
        "agent",
    )


    return graph.compile()


graph = build_graph()