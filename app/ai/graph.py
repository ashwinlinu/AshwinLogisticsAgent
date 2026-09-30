from langgraph.graph import StateGraph, MessagesState, START, END

from app.ai.nodes.rag import rag_node


def build_graph():

    graph = StateGraph(MessagesState)

    graph.add_node("rag", rag_node)

    graph.add_edge(START, "rag")
    graph.add_edge("rag", END)

    return graph.compile()


graph = build_graph()