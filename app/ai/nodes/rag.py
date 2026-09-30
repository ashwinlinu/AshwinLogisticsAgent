from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, AIMessage

from app.rag.context import format_retrieved_context
from app.rag.retriever import retrieve
from app.ai.client import client
from app.config.settings import settings


SYSTEM_PROMPT = """
You are the AI Support Agent for Ashwin Logistics.

Answer the user's question using the provided internal knowledge
context.

Rules:
1. Use the provided context as the source of truth.
2. Do not invent logistics policies, shipment information, fees,
   procedures, or operational facts.
3. If the context does not contain enough information to answer,
   clearly say that the information is not available.
4. Do not claim that you performed an action unless a tool actually
   performed that action.
5. Keep the answer concise and useful for a support or operations user.
6. When appropriate, mention the relevant policy or document.
"""


async def rag_node(state: MessagesState) -> MessagesState:

    query = state["messages"][-1].content

    results = retrieve(
        query=query,
        top_k=5,
    )

    context = format_retrieved_context(results)

    response = await client.responses.create(
        model=settings.azure_openai_deployment,
        instructions=SYSTEM_PROMPT,
        input=f"""
        Internal knowledge context:

        {context}

        User question:

        {query}
        """,
            )

    answer = response.output_text

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }