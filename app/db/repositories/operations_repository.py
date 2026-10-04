from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db.collections import BOOKINGS_COLLECTION, CUSTOMERS_COLLECTION, SHIPMENTS_COLLECTION
from app.db.mongodb import get_db


class OperationsRepository:
    @property
    def customers(self):
        return get_db()[CUSTOMERS_COLLECTION]

    @property
    def bookings(self):
        return get_db()[BOOKINGS_COLLECTION]

    @property
    def shipments(self):
        return get_db()[SHIPMENTS_COLLECTION]

    async def ensure_indexes(self):
        await self.customers.create_index([("user_id", 1), ("customer_id", 1)], unique=True)
        await self.customers.create_index([("user_id", 1), ("created_at", -1)])
        await self.bookings.create_index([("user_id", 1), ("booking_id", 1)], unique=True)
        await self.bookings.create_index([("user_id", 1), ("customer_id", 1)])
        await self.shipments.create_index([("user_id", 1), ("shipment_id", 1)], unique=True)
        await self.shipments.create_index([("user_id", 1), ("customer_id", 1)])

    async def create_customer(self, user_id: str, values: dict) -> dict:
        record = {"customer_id": f"CUS-{uuid4().hex[:12].upper()}", "user_id": user_id, **values, "created_at": datetime.now(timezone.utc)}
        await self.customers.insert_one(record)
        return record

    async def list_customers(self, user_id: str) -> list[dict]:
        return await self.customers.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).to_list(length=500)

    async def get_customer(self, user_id: str, customer_id: str) -> dict | None:
        return await self.customers.find_one({"user_id": user_id, "customer_id": customer_id}, {"_id": 0})

    async def update_customer(self, user_id: str, customer_id: str, values: dict) -> dict | None:
        values = {key: value for key, value in values.items() if value is not None}
        values["updated_at"] = datetime.now(timezone.utc)
        record = await self.customers.find_one_and_update({"user_id": user_id, "customer_id": customer_id}, {"$set": values}, return_document=True)
        return {key: value for key, value in record.items() if key != "_id"} if record else None

    async def delete_customer(self, user_id: str, customer_id: str) -> bool:
        # Keep referential integrity: customer records with bookings cannot be deleted.
        if await self.bookings.find_one({"user_id": user_id, "customer_id": customer_id}):
            return False
        return (await self.customers.delete_one({"user_id": user_id, "customer_id": customer_id})).deleted_count > 0

    async def create_booking(self, user_id: str, values: dict) -> dict | None:
        customer_id = values["customer_id"]
        if await self.get_customer(user_id, customer_id) is None:
            return None
        record = {"booking_id": f"BKG-{uuid4().hex[:12].upper()}", "user_id": user_id, "customer_id": customer_id, "shipment_ids": [], **{k: v for k, v in values.items() if k != "customer_id"}, "created_at": datetime.now(timezone.utc)}
        await self.bookings.insert_one(record)
        return record

    async def list_bookings(self, user_id: str, customer_id: str | None = None) -> list[dict]:
        query = {"user_id": user_id}
        if customer_id:
            query["customer_id"] = customer_id
        return await self.bookings.find(query, {"_id": 0}).sort("created_at", -1).to_list(length=500)

    async def get_booking(self, user_id: str, booking_id: str) -> dict | None:
        return await self.bookings.find_one({"user_id": user_id, "booking_id": booking_id}, {"_id": 0})

    async def create_shipment(self, user_id: str, values: dict) -> dict | None:
        booking = await self.get_booking(user_id, values["booking_id"])
        if booking is None:
            return None
        now = datetime.now(timezone.utc)
        record = {"shipment_id": f"SHP-{uuid4().hex[:12].upper()}", "user_id": user_id, "customer_id": booking["customer_id"], "booking_id": booking["booking_id"], "status": values["status"], "origin": values["origin"], "destination": values["destination"], "carrier": values["carrier"], "estimated_delivery": values.get("estimated_delivery"), "last_update": values.get("last_update"), "updated_at": now}
        await self.shipments.insert_one(record)
        await self.bookings.update_one({"user_id": user_id, "booking_id": booking["booking_id"]}, {"$addToSet": {"shipment_ids": record["shipment_id"]}})
        return record

    async def get_shipment(self, user_id: str, shipment_id: str) -> dict | None:
        return await self.shipments.find_one({"user_id": user_id, "shipment_id": shipment_id}, {"_id": 0})

    async def list_shipments(self, user_id: str, customer_id: str | None = None) -> list[dict]:
        query = {"user_id": user_id}
        if customer_id:
            query["customer_id"] = customer_id
        return await self.shipments.find(query, {"_id": 0}).sort("updated_at", -1).to_list(length=500)


operations_repository = OperationsRepository()
