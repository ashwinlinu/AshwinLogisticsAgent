from datetime import datetime, timedelta, timezone

import asyncio

from app.api.auth import current_identity
from app.db.repositories import auth_repository as auth_repository_module
from app.db.repositories.auth_repository import AuthRepository, _hash_password, _verify_password
from fastapi.security import HTTPAuthorizationCredentials


class Collection:
    def __init__(self, find_result=None):
        self.find_result = find_result
        self.query = None
        self.inserted = None
        self.updated = None

    async def find_one(self, query, *args, **kwargs):
        self.query = query
        return self.find_result

    async def insert_one(self, document):
        self.inserted = document

    async def update_one(self, query, update):
        self.updated = (query, update)


class Database(dict):
    def __getitem__(self, key):
        return super().__getitem__(key)


def test_password_hash_is_salted_and_verifiable():
    first = _hash_password("safe passphrase 123")
    second = _hash_password("safe passphrase 123")
    assert first != second
    assert _verify_password("safe passphrase 123", first)
    assert not _verify_password("wrong password", first)
    assert "safe passphrase" not in first


def test_new_session_stores_only_token_hash(monkeypatch):
    sessions = Collection()
    db = Database(sessions=sessions)
    monkeypatch.setattr(auth_repository_module, "get_db", lambda: db)
    token, record = asyncio.run(AuthRepository().create_session("USR-1"))
    assert token
    assert sessions.inserted["token_hash"] != token
    assert len(sessions.inserted["token_hash"]) == 64
    assert "token_hash" not in record
    assert record["expires_at"] > record["created_at"]


def test_token_lookup_requires_active_unexpired_session(monkeypatch):
    sessions = Collection(find_result=None)
    db = Database(sessions=sessions, users=Collection())
    monkeypatch.setattr(auth_repository_module, "get_db", lambda: db)
    result = asyncio.run(AuthRepository().get_user_for_token("opaque-token"))
    assert result is None
    assert sessions.query["is_active"] is True
    assert sessions.query["expires_at"]["$gt"] <= datetime.now(timezone.utc)
    assert sessions.query["token_hash"] != "opaque-token"


def test_valid_token_resolves_user_and_updates_last_activity(monkeypatch):
    now = datetime.now(timezone.utc)
    session_doc = {"_id": "mongo-id", "session_id": "AUTH-1", "user_id": "USR-1", "token_hash": "hash", "created_at": now, "last_activity_at": now, "expires_at": now + timedelta(hours=1), "is_active": True}
    user_doc = {"_id": "user-mongo", "user_id": "USR-1", "email": "user@example.com", "password_hash": "secret-hash", "status": "active"}
    sessions, users = Collection(session_doc), Collection(user_doc)
    db = Database(sessions=sessions, users=users)
    monkeypatch.setattr(auth_repository_module, "get_db", lambda: db)
    identity = asyncio.run(AuthRepository().get_user_for_token("opaque-token"))
    assert identity[0]["user_id"] == "USR-1"
    assert "password_hash" not in identity[0]
    assert identity[1]["session_id"] == "AUTH-1"
    assert sessions.updated[1]["$set"]["last_activity_at"] >= now


def test_current_identity_resolves_bearer_credentials(monkeypatch):
    expected = ({"user_id": "USR-1"}, {"session_id": "AUTH-1"})
    calls = []
    async def lookup(token):
        calls.append(token)
        return expected
    monkeypatch.setattr(auth_repository_module.auth_repository, "get_user_for_token", lookup)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="opaque")
    identity = asyncio.run(current_identity(credentials))
    assert identity == {"user": expected[0], "session": expected[1]}
    assert calls == ["opaque"]
