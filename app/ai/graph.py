from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.ai.llm import llm


class AgentState(TypedDict):
    message: str
    response: str


async def agent_node(state: AgentState) -> AgentState:
    response = await llm.ainvoke(state["message"])

    return {
        "message": state["message"],
        "response": response.content,
    }


builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

graph = builder.compile()