from langgraph.graph import MessagesState, START, END, StateGraph

from app.ai.llm import llm
from app.ai.prompts.agent import agent_prompt


async def agent_node(state: MessagesState):

    messages = agent_prompt.invoke({
        "messages": state["messages"]
    })
    
    response = await llm.ainvoke(messages)

    return {
        "messages": [response]
    }


builder = StateGraph(MessagesState)

builder.add_node("agent", agent_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

graph = builder.compile()