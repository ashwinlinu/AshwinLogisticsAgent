import asyncio
import json
from pathlib import Path

from app.db.mongodb import db
from app.db.collections import SHIPMENTS_COLLECTION


SEED_FILE = Path("data/seed/shipments.json")


async def main():
    print("Loading shipment seed data...")

    with open(SEED_FILE, "r", encoding="utf-8") as file:
        shipments = json.load(file)

    collection = db[SHIPMENTS_COLLECTION]

    await collection.delete_many({})

    if shipments:
        result = await collection.insert_many(shipments)
        print(f"Inserted shipments: {len(result.inserted_ids)}")
    else:
        print("No shipments found")


if __name__ == "__main__":
    asyncio.run(main())