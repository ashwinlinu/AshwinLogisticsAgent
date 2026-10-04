import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

from app.db.collections import BOOKINGS_COLLECTION, CUSTOMERS_COLLECTION, SHIPMENTS_COLLECTION, USERS_COLLECTION
from app.db.mongodb import get_db
from app.db.repositories.auth_repository import _hash_password, auth_repository


SEED_DIR = Path("data/seed")
load_dotenv()


async def main():
    seed_password = os.getenv("SEED_OWNER_PASSWORD")
    if not seed_password or len(seed_password) < 12:
        raise RuntimeError("Set SEED_OWNER_PASSWORD to a password of at least 12 characters before seeding.")
    db = get_db()
    await auth_repository.ensure_indexes()
    owner = {
        "user_id": "USR-1001",
        "email": "ashwin@ashwinlogistics.com",
        "password_hash": _hash_password(seed_password),
        "full_name": "Ashwin",
        "role": "admin",
        "status": "active",
    }
    await db[USERS_COLLECTION].update_one(
        {"user_id": owner["user_id"]},
        {"$setOnInsert": {**owner, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    for filename, collection_name in (("customers.json", CUSTOMERS_COLLECTION), ("bookings.json", BOOKINGS_COLLECTION), ("shipments.json", SHIPMENTS_COLLECTION)):
        with (SEED_DIR / filename).open("r", encoding="utf-8") as file:
            records = json.load(file)
        for record in records:
            record["user_id"] = owner["user_id"]
            key = next(key for key in ("customer_id", "booking_id", "shipment_id") if key in record)
            await db[collection_name].update_one({key: record[key]}, {"$set": record}, upsert=True)
        print(f"Seeded {len(records)} records into {collection_name}")


if __name__ == "__main__":
    asyncio.run(main())
