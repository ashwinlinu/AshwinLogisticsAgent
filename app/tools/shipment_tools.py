from __future__ import annotations

import logging

from langchain_core.tools import tool

from app.db.repositories.shipment_repository import shipment_repository

logger = logging.getLogger(__name__)


def _normalize_shipment_id(shipment_id: str | None) -> str | None:
    if shipment_id is None:
        return None

    normalized = shipment_id.strip().upper()
    if not normalized:
        return None

    return normalized


@tool
async def get_shipment_status(shipment_id: str) -> dict:
    """
    Retrieve the current operational status and details of a shipment.

    Use this tool when the user asks about a specific shipment,
    including its current status, origin, destination, estimated
    delivery, or latest update.

    Args:
        shipment_id: Shipment reference such as SHP-1001.
    """
    try:
        normalized_id = _normalize_shipment_id(shipment_id)

        if normalized_id is None:
            return {
                "status": "invalid_input",
                "message": "Please provide a valid shipment ID.",
            }

        if not normalized_id.startswith("SHP-") or len(normalized_id) < 8:
            return {
                "status": "invalid_input",
                "message": "Invalid shipment ID format. Example: SHP-1001",
                "shipment_id": normalized_id,
            }

        shipment = await shipment_repository.get_shipment(normalized_id)

        if shipment is None:
            return {
                "status": "not_found",
                "shipment_id": normalized_id,
                "message": "Shipment not found.",
            }

        return {
            "status": "ok",
            "shipment": shipment,
        }

    except Exception:
        logger.exception("Shipment status tool failed")
        return {
            "status": "error",
            "message": "The shipment service is temporarily unavailable.",
        }