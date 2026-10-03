import asyncio

from langchain_core.messages import HumanMessage

from app.ai.graph import graph


async def main():
    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="what is the policy of canceling a shipment?"
                )
            ]
        }
    )

    for message in result["messages"]:
        print(f"{message.type}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())