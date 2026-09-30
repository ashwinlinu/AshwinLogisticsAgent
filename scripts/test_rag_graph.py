
from langchain_core.messages import HumanMessage

from app.ai.graph import graph


async def main():
    question = "What happens if a customer cancels less than two hours before pickup?"

    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        }
    )

    print("=" * 70)
    print("RAG GRAPH TEST")
    print("=" * 70)

    for message in result["messages"]:
        print(f"{message.type}: {message.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

