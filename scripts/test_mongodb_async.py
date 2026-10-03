import asyncio

from app.db.mongodb import ping_mongodb


async def main():
    print("Testing async MongoDB connection...")

    result = await ping_mongodb()

    print(f"MongoDB ping: {result}")


if __name__ == "__main__":
    asyncio.run(main())