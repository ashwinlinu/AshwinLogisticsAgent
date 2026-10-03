from __future__ import annotations

import asyncio

from app.ai.service import ai_service
from app.db.repositories.conversation_repository import conversation_repository, resolve_user_id


async def _clear_user_conversations(user_id: str):
    convs = await conversation_repository.list_user_conversations(user_id=user_id, limit=50)
    for conv in convs:
        await conversation_repository.collection.delete_one({"conversation_id": conv.conversation_id})


def test_default_user_id_is_used_for_conversations():
    assert resolve_user_id(None) == "ashwinlinu"
    assert resolve_user_id("") == "ashwinlinu"


def test_conversation_repository_uses_default_user():
    assert resolve_user_id("ashwinlinu") == "ashwinlinu"


def test_user_conversation_history_can_be_retrieved():
    user_id = "ashwinlinu"
    asyncio.run(_clear_user_conversations(user_id))

    conv = asyncio.run(conversation_repository.create_conversation(user_id=user_id))
    asyncio.run(conversation_repository.append_message(conv.conversation_id, "user", "What is the status of SHP-1001?"))
    asyncio.run(conversation_repository.append_message(conv.conversation_id, "assistant", "In transit."))

    history = asyncio.run(conversation_repository.get_history(conv.conversation_id))
    assert len(history) == 2
    assert history[0].content == "What is the status of SHP-1001?"
    assert history[1].content == "In transit."

    asyncio.run(_clear_user_conversations(user_id))


def test_ai_service_uses_latest_user_conversation_when_no_id_is_sent():
    user_id = "ashwinlinu"
    asyncio.run(_clear_user_conversations(user_id))

    first = asyncio.run(conversation_repository.create_conversation(user_id=user_id))
    asyncio.run(conversation_repository.append_message(first.conversation_id, "user", "What is status of SHP-1001?"))
    asyncio.run(conversation_repository.append_message(first.conversation_id, "assistant", "It is in transit."))

    response, conversation_id = asyncio.run(ai_service.generate_response("Where is it going?", user_id=user_id))
    assert conversation_id == first.conversation_id
    assert isinstance(response, str)

    asyncio.run(_clear_user_conversations(user_id))
