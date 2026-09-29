import asyncio

from app.ai.graph import graph


async def main():
    result = await graph.ainvoke(
        {
            "message": "Introduce yourself as the AI support agent for Ashwin Logistics.",
            "response": "",
        }
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())