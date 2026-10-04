from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from uuid import uuid4

from app.db.collections import SESSIONS_COLLECTION, USERS_COLLECTION
from app.db.mongodb import get_db

SESSION_LIFETIME = timedelta(hours=12)
PBKDF2_ITERATIONS = 310_000


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations)).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _public_user(user: dict) -> dict:
    return {key: value for key, value in user.items() if key not in {"_id", "password_hash"}}


class AuthRepository:
    @property
    def users(self):
        return get_db()[USERS_COLLECTION]

    @property
    def sessions(self):
        return get_db()[SESSIONS_COLLECTION]

    async def ensure_indexes(self):
        await self.users.create_index("email", unique=True)
        await self.users.create_index("user_id", unique=True)
        await self.sessions.create_index("token_hash", unique=True)
        await self.sessions.create_index("session_id", unique=True)
        await self.sessions.create_index([("user_id", 1), ("created_at", -1)])

    async def register(self, email: str, password: str, full_name: str) -> dict | None:
        normalized_email = email.strip().lower()
        if await self.users.find_one({"email": normalized_email}):
            return None
        now = datetime.now(timezone.utc)
        user = {
            "user_id": f"USR-{uuid4().hex[:12].upper()}",
            "email": normalized_email,
            "password_hash": _hash_password(password),
            "full_name": full_name.strip(),
            "role": "operator",
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        try:
            await self.users.insert_one(user)
        except Exception as exc:
            if getattr(exc, "code", None) == 11000:
                return None
            raise
        return _public_user(user)

    async def authenticate(self, email: str, password: str) -> dict | None:
        user = await self.users.find_one({"email": email.strip().lower()})
        if not user or user.get("status") != "active" or not _verify_password(password, user.get("password_hash", "")):
            return None
        return _public_user(user)

    async def create_session(self, user_id: str) -> tuple[str, dict]:
        token = secrets.token_urlsafe(36)
        now = datetime.now(timezone.utc)
        session = {
            "session_id": str(uuid4()),
            "user_id": user_id,
            "token_hash": hashlib.sha256(token.encode()).hexdigest(),
            "created_at": now,
            "last_activity_at": now,
            "expires_at": now + SESSION_LIFETIME,
            "is_active": True,
        }
        await self.sessions.insert_one(session)
        return token, {key: value for key, value in session.items() if key not in {"_id", "token_hash"}}

    async def get_user_for_token(self, token: str) -> tuple[dict, dict] | None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        session = await self.sessions.find_one({"token_hash": token_hash, "is_active": True, "expires_at": {"$gt": now}})
        if session is None:
            return None
        user = await self.users.find_one({"user_id": session["user_id"], "status": "active"})
        if user is None:
            await self.sessions.update_one({"_id": session["_id"]}, {"$set": {"is_active": False}})
            return None
        await self.sessions.update_one({"_id": session["_id"]}, {"$set": {"last_activity_at": now}})
        return _public_user(user), {key: value for key, value in session.items() if key not in {"_id", "token_hash"}}

    async def revoke_session(self, session_id: str, user_id: str) -> bool:
        result = await self.sessions.update_one({"session_id": session_id, "user_id": user_id, "is_active": True}, {"$set": {"is_active": False}})
        return result.modified_count > 0

    async def list_sessions(self, user_id: str) -> list[dict]:
        docs = await self.sessions.find({"user_id": user_id}, {"_id": 0, "token_hash": 0}).sort("created_at", -1).limit(100).to_list(length=100)
        return docs

    async def refresh_session(self, session_id: str, user_id: str) -> dict | None:
        now = datetime.now(timezone.utc)
        result = await self.sessions.find_one_and_update(
            {"session_id": session_id, "user_id": user_id, "is_active": True, "expires_at": {"$gt": now}},
            {"$set": {"last_activity_at": now, "expires_at": now + SESSION_LIFETIME}},
            return_document=True,
        )
        if result is None:
            return None
        return {key: value for key, value in result.items() if key not in {"_id", "token_hash"}}


auth_repository = AuthRepository()
