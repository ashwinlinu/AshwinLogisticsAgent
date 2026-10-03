from __future__ import annotations

from datetime import datetime, timezone

from app.db.mongodb import get_db
from app.models.chat import ChatMessage, ConversationRecord

CONVERSATIONS_COLLECTION = "conversations"
DEFAULT_USER_ID = "ashwinlinu"


def resolve_user_id(user_id: str | None) -> str:
    return (user_id or DEFAULT_USER_ID).strip() or DEFAULT_USER_ID


class ConversationRepository:
    def __init__(self):
        self._collection_name = CONVERSATIONS_COLLECTION

    @property
    def collection(self):
        return get_db()[self._collection_name]

    def _get_collection(self):
        return self.collection

    async def create_conversation(self, user_id: str | None = None, session_id: str | None = None) -> ConversationRecord:
        resolved_user_id = resolve_user_id(user_id)
        record = ConversationRecord.from_session(user_id=resolved_user_id, session_id=session_id)
        await self._get_collection().insert_one(record.model_dump(mode="json"))
        return record

    async def get_conversation(self, conversation_id: str) -> ConversationRecord | None:
        document = await self._get_collection().find_one({"conversation_id": conversation_id})
        if document is None:
            return None
        return ConversationRecord.model_validate(document)

    async def get_session(self, session_id: str) -> ConversationRecord | None:
        document = await self._get_collection().find_one({"session_id": session_id})
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

    async def list_user_conversations(self, user_id: str | None = None, limit: int = 20) -> list[ConversationRecord]:
        resolved_user_id = resolve_user_id(user_id)
        documents = await self._get_collection().find({"user_id": resolved_user_id}).sort("updated_at", -1).limit(limit).to_list(length=limit)
        return [ConversationRecord.model_validate(document) for document in documents]

    async def append_message(self, conversation_id: str, role: str, content: str) -> None:
        message = ChatMessage(role=role, content=content)

        await self._get_collection().update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": message.model_dump(mode="json")},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            upsert=True,
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
