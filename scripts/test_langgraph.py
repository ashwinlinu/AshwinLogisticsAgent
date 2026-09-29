import asyncio

from langchain_core.messages import HumanMessage

from app.ai.graph import graph


async def main():
    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="What is the current status of shipment SHP-1001?"
                )
            ]
        }
    )

    for message in result["messages"]:
        print(f"{message.type}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())