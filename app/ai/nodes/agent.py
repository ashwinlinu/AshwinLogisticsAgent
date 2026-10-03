from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.ai.client import token_provider

from app.tools.shipment_tools import get_shipment_status
from app.tools.rag_tools import search_internal_knowledge


SYSTEM_PROMPT = """
You are the AI Support Agent for Ashwin Logistics.

You help users with:

- Internal logistics policies and procedures
- Shipment information
- Support and operations questions

TOOLS

1. get_shipment_status

Use this tool when the user asks about:

- shipment status
- shipment location
- shipment tracking
- shipment delivery status
- shipment ETA

Example:

"What is the status of SHP-1001?"

2. search_internal_knowledge

Use this tool when the user asks about:

- cancellation policies
- booking procedures
- claims
- damaged shipments
- documentation
- compliance
- support procedures
- internal logistics policies
- operational procedures

Example:

"What happens if a customer cancels less than two hours
before pickup?"

Do NOT use the shipment tool for policy questions.

Do NOT invent shipment information or company policies.

If the shipment tool says that a shipment was not found,
tell the user clearly that the shipment was not found.

For simple conversational questions such as:

- Who are you?
- Hello
- What can you help me with?

answer directly without using a tool.
"""


llm = ChatOpenAI(
    model=settings.azure_openai_deployment,
    base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)

llm_with_tools = llm.bind_tools(
    [
        get_shipment_status,
        search_internal_knowledge,
    ]
)


async def agent_node(state: MessagesState):

    messages = state["messages"]

    response = await llm_with_tools.ainvoke(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *messages,
        ]
    )

    return {
        "messages": [response],
    }