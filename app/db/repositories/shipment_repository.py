from typing import Optional

from app.db.collections import SHIPMENTS_COLLECTION
from app.db.mongodb import get_db


class ShipmentRepository:

    def __init__(self):
        self.collection = None

    def _get_collection(self):
        return get_db()[SHIPMENTS_COLLECTION]

    async def get_shipment(
        self,
        shipment_id: str,
        user_id: str | None = None,
    ) -> Optional[dict]:

        shipment_id = shipment_id.strip().upper()

        query = {"shipment_id": shipment_id}
        if user_id is not None:
            query["user_id"] = user_id
        shipment = await self._get_collection().find_one(
            query,
            {
                "_id": 0
            },
        )

        return shipment


shipment_repository = ShipmentRepository()
