from __future__ import annotations

from datetime import datetime, timezone

from app.db.mongodb import get_db
from app.db.collections import CONVERSATIONS_COLLECTION
from app.models.chat import ChatMessage, ConversationRecord

def resolve_user_id(user_id: str | None) -> str:
    if not user_id or not user_id.strip():
        raise ValueError("An authenticated user_id is required")
    return user_id.strip()


class ConversationRepository:
    def __init__(self):
        self._collection_name = CONVERSATIONS_COLLECTION

    @property
    def collection(self):
        return get_db()[self._collection_name]

    def _get_collection(self):
        return self.collection

    async def ensure_indexes(self):
        await self._get_collection().create_index([("user_id", 1), ("auth_session_id", 1), ("updated_at", -1)])
        await self._get_collection().create_index([("user_id", 1), ("conversation_id", 1)], unique=True)

    async def create_conversation(self, user_id: str | None = None, session_id: str | None = None, auth_session_id: str | None = None) -> ConversationRecord:
        resolved_user_id = resolve_user_id(user_id)
        record = ConversationRecord.from_session(user_id=resolved_user_id, session_id=session_id, auth_session_id=auth_session_id)
        await self._get_collection().insert_one(record.model_dump(mode="json"))
        return record

    async def get_conversation(self, conversation_id: str, user_id: str | None = None) -> ConversationRecord | None:
        query = {"conversation_id": conversation_id}
        if user_id is not None:
            query["user_id"] = user_id
        document = await self._get_collection().find_one(query)
        if document is None:
            return None
        return ConversationRecord.model_validate(document)

    async def get_session(self, session_id: str, user_id: str | None = None) -> ConversationRecord | None:
        query = {"session_id": session_id}
        if user_id is not None:
            query["user_id"] = user_id
        document = await self._get_collection().find_one(query)
        if document is None:
            return None
        return ConversationRecord.model_validate(document)

    async def get_latest_conversation_for_user(self, user_id: str | None = None) -> ConversationRecord | None:
        resolved_user_id = resolve_user_id(user_id)
        document = await self._get_collection().find_one(
            {"user_id": resolved_user_id},
            sort=[("updated_at", -1)],
        )
        if document is None:
            return None
        return ConversationRecord.model_validate(document)

    async def get_latest_session_for_user(self, user_id: str | None = None) -> ConversationRecord | None:
        return await self.get_latest_conversation_for_user(user_id=user_id)

    async def get_latest_conversation_for_auth_session(self, user_id: str, auth_session_id: str) -> ConversationRecord | None:
        document = await self._get_collection().find_one(
            {"user_id": user_id, "auth_session_id": auth_session_id}, sort=[("updated_at", -1)]
        )
        return ConversationRecord.model_validate(document) if document else None

    async def list_user_conversations(self, user_id: str | None = None, limit: int = 20) -> list[ConversationRecord]:
        resolved_user_id = resolve_user_id(user_id)
        documents = await self._get_collection().find({"user_id": resolved_user_id}).sort("updated_at", -1).limit(limit).to_list(length=limit)
        return [ConversationRecord.model_validate(document) for document in documents]

    async def append_message(self, conversation_id: str, role: str, content: str, user_id: str | None = None) -> None:
        message = ChatMessage(role=role, content=content)

        await self._get_collection().update_one(
            {"conversation_id": conversation_id, **({"user_id": user_id} if user_id else {})},
            {
                "$push": {"messages": message.model_dump(mode="json")},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            upsert=user_id is None,
        )

    async def get_history(self, conversation_id: str) -> list[ChatMessage]:
        document = await self._get_collection().find_one({"conversation_id": conversation_id})
        if document is None:
            return []
        return [ChatMessage.model_validate(item) for item in document.get("messages", [])]

    async def ensure_session(self, user_id: str | None = None, session_id: str | None = None) -> ConversationRecord:
        resolved_user_id = resolve_user_id(user_id)
        session_id = session_id or str(datetime.now(timezone.utc).timestamp())
        conversation = await self.get_session(session_id=session_id)

        if conversation is None:
            conversation = await self.create_conversation(user_id=resolved_user_id, session_id=session_id)

        return conversation


conversation_repository = ConversationRepository()
