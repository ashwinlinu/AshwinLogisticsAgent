from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.ai.service import AIService
from app.db.repositories import conversation_repository as conversation_repository_module
from app.models.chat import ConversationRecord


def test_user_identity_is_required_for_conversation_ownership():
    assert conversation_repository_module.resolve_user_id("USR-1") == "USR-1"
    with pytest.raises(ValueError, match="authenticated user_id"):
        conversation_repository_module.resolve_user_id(None)
    with pytest.raises(ValueError, match="authenticated user_id"):
        conversation_repository_module.resolve_user_id(" ")


def test_conversation_record_includes_owner_and_auth_session():
    record = ConversationRecord.from_session(user_id="USR-1", auth_session_id="AUTH-1")
    assert record.user_id == "USR-1"
    assert record.auth_session_id == "AUTH-1"
    assert record.session_id
    assert record.conversation_id == record.session_id


def test_ai_service_creates_session_scoped_conversation(monkeypatch):
    record = ConversationRecord.from_session(user_id="USR-1", auth_session_id="AUTH-1")
    created = []
    appends = []
    async def no_existing(*args, **kwargs):
        return None
    async def create(**kwargs):
        created.append(kwargs)
        return record
    async def empty_history(conversation_id):
        return []
    async def append(*args, **kwargs):
        appends.append((args, kwargs))
    async def invoke(state, config):
        assert config["configurable"]["user_id"] == "USR-1"
        return {"messages": [SimpleNamespace(content="Assistant reply") ]}

    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_latest_conversation_for_auth_session", no_existing)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "create_conversation", create)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_history", empty_history)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "append_message", append)
    monkeypatch.setattr("app.ai.service.graph.ainvoke", invoke)

    response, conversation_id = asyncio.run(AIService().generate_response("Hello", user_id="USR-1", auth_session_id="AUTH-1"))
    assert response == "Assistant reply"
    assert conversation_id == record.conversation_id
    assert created == [{"user_id": "USR-1", "session_id": None, "auth_session_id": "AUTH-1"}]
    assert len(appends) == 2
    assert all(entry[1]["user_id"] == "USR-1" for entry in appends)


def test_session_scoped_lookup_cannot_fall_back_to_another_user(monkeypatch):
    record = ConversationRecord.from_session(user_id="USR-A", auth_session_id="AUTH-A")
    lookups = []
    async def no_existing(*args, **kwargs):
        lookups.append((args, kwargs))
        return None
    async def create(**kwargs):
        assert kwargs["user_id"] == "USR-A"
        assert kwargs["auth_session_id"] == "AUTH-A"
        return record
    async def empty_history(conversation_id):
        return []
    async def append(*args, **kwargs):
        return None
    async def invoke(state, config):
        return {"messages": [SimpleNamespace(content="Response")]}

    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_latest_conversation_for_auth_session", no_existing)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "create_conversation", create)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_history", empty_history)
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "append_message", append)
    monkeypatch.setattr("app.ai.service.graph.ainvoke", invoke)
    _, conversation_id = asyncio.run(AIService().generate_response("Hi", user_id="USR-A", auth_session_id="AUTH-A"))
    assert conversation_id == record.conversation_id
    assert lookups == [( ("USR-A", "AUTH-A"), {})]
