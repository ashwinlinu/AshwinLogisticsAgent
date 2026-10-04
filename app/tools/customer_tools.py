from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from app.db.repositories.operations_repository import operations_repository


@tool
async def find_customer(name_or_email: str, config: RunnableConfig) -> dict:
    """Find a customer owned by the authenticated user by name, email, or company."""
    user_id = (config.get("configurable") or {}).get("user_id")
    if not user_id:
        return {"status": "unauthorized"}
    customers = await operations_repository.list_customers(user_id)
    term = name_or_email.strip().casefold()
    matches = [c for c in customers if term in " ".join(str(c.get(k, "")) for k in ("name", "email", "company")).casefold()]
    return {"status": "ok", "customers": matches[:10]}


@tool
async def get_customer_shipments(customer_id: str, config: RunnableConfig) -> dict:
    """List shipments for a customer owned by the authenticated user."""
    user_id = (config.get("configurable") or {}).get("user_id")
    if not user_id:
        return {"status": "unauthorized"}
    if await operations_repository.get_customer(user_id, customer_id) is None:
        return {"status": "not_found", "message": "Customer not found."}
    shipments = await operations_repository.list_shipments(user_id, customer_id)
    return {"status": "ok", "customer_id": customer_id, "shipments": shipments}
