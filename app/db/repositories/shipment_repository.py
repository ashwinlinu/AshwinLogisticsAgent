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
    ) -> Optional[dict]:

        shipment_id = shipment_id.strip().upper()

        shipment = await self._get_collection().find_one(
            {
                "shipment_id": shipment_id
            },
            {
                "_id": 0
            },
        )

        return shipment


shipment_repository = ShipmentRepository()