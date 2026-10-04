from datetime import datetime, timezone

from app.db.collections import AUDIT_LOG_COLLECTION
from app.db.mongodb import get_db


async def record_audit(user_id: str, action: str, resource_type: str, resource_id: str | None = None) -> None:
    await get_db()[AUDIT_LOG_COLLECTION].insert_one({
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "created_at": datetime.now(timezone.utc),
    })


async def ensure_audit_indexes() -> None:
    await get_db()[AUDIT_LOG_COLLECTION].create_index([("user_id", 1), ("created_at", -1)])
