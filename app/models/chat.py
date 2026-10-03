from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationRecord(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list[ChatMessage] = Field(default_factory=list)

    @classmethod
    def from_session(cls, user_id: str | None = None, session_id: str | None = None):
        session_value = session_id or str(uuid4())
        return cls(
            session_id=session_value,
            conversation_id=session_value,
            user_id=user_id,
        )
