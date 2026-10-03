import asyncio

from app.db.mongodb import db
from app.db.collections import SHIPMENTS_COLLECTION


async def main():
    collection = db[SHIPMENTS_COLLECTION]

    shipments = await collection.find({}).to_list(length=None)

    print("=" * 60)
    print("SHIPMENTS")
    print("=" * 60)

    for shipment in shipments:
        print(
            shipment["shipment_id"],
            "->",
            shipment["status"],
        )


if __name__ == "__main__":
    asyncio.run(main())