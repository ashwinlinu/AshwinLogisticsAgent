import asyncio

from app.db.repositories.conversation_repository import conversation_repository


async def main():
    user_id = "ashwinlinu"
    await conversation_repository.collection.delete_many({"user_id": user_id})

    conv = await conversation_repository.create_conversation(user_id=user_id)
    await conversation_repository.append_message(conv.conversation_id, "user", "What is the status of SHP-1001?")
    await conversation_repository.append_message(conv.conversation_id, "assistant", "SHP-1001 is in transit.")
    await conversation_repository.append_message(conv.conversation_id, "user", "Where is it going?")
    await conversation_repository.append_message(conv.conversation_id, "assistant", "It is currently moving toward Dallas.")

    print(f"Created seeded conversation for {user_id}: {conv.conversation_id}")


if __name__ == "__main__":
    asyncio.run(main())
