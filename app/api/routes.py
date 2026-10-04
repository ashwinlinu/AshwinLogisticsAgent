import logging
import time
from collections import defaultdict, deque
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.ai.service import ai_service
from app.api.auth import current_identity
from app.api.models import BookingCreate, ChatRequest, ChatResponse, CustomerCreate, CustomerUpdate, LoginRequest, RegisterRequest, ShipmentCreate
from app.db.repositories.auth_repository import auth_repository
from app.db.repositories.audit_repository import record_audit
from app.db.repositories.conversation_repository import conversation_repository
from app.db.repositories.operations_repository import operations_repository

logger = logging.getLogger("app.api.routes")
router = APIRouter()
_auth_attempts: dict[str, deque[float]] = defaultdict(deque)


def _limit_auth_attempts(request: Request):
    """Bound registration/login attempts per process and source IP."""
    now = time.monotonic()
    key = request.client.host if request.client else "unknown"
    attempts = _auth_attempts[key]
    while attempts and now - attempts[0] > 60:
        attempts.popleft()
    if len(attempts) >= 10:
        raise HTTPException(status_code=429, detail="Too many authentication attempts. Try again shortly.")
    attempts.append(now)


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request):
    _limit_auth_attempts(request)
    user = await auth_repository.register(payload.email, payload.password, payload.full_name)
    if user is None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    token, session = await auth_repository.create_session(user["user_id"])
    await record_audit(user["user_id"], "account.register", "user", user["user_id"])
    await record_audit(user["user_id"], "session.create", "session", session["session_id"])
    return {"user": user, "access_token": token, "token_type": "bearer", "session": session}


@router.post("/auth/login")
async def login(payload: LoginRequest, request: Request):
    _limit_auth_attempts(request)
    user = await auth_repository.authenticate(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})
    token, session = await auth_repository.create_session(user["user_id"])
    await record_audit(user["user_id"], "session.create", "session", session["session_id"])
    return {"user": user, "access_token": token, "token_type": "bearer", "session": session}


@router.get("/auth/me")
async def me(identity: dict = Depends(current_identity)):
    return {"user": identity["user"], "session": identity["session"]}


@router.post("/auth/logout")
async def logout(identity: dict = Depends(current_identity)):
    await auth_repository.revoke_session(identity["session"]["session_id"], identity["user"]["user_id"])
    await record_audit(identity["user"]["user_id"], "session.revoke", "session", identity["session"]["session_id"])
    return {"status": "ok"}


@router.get("/sessions")
async def list_sessions(identity: dict = Depends(current_identity)):
    sessions = await auth_repository.list_sessions(identity["user"]["user_id"])
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, identity: dict = Depends(current_identity)):
    for session in await auth_repository.list_sessions(identity["user"]["user_id"]):
        if session["session_id"] == session_id:
            return session
    raise HTTPException(status_code=404, detail="Session not found.")


@router.post("/sessions/refresh")
async def refresh_session(identity: dict = Depends(current_identity)):
    session = await auth_repository.refresh_session(identity["session"]["session_id"], identity["user"]["user_id"])
    if session is None:
        raise HTTPException(status_code=401, detail="Session is invalid or expired.")
    await record_audit(identity["user"]["user_id"], "session.refresh", "session", session["session_id"])
    return {"session": session}


@router.post("/ai/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request, identity: dict = Depends(current_identity)):
    request_id = getattr(request.state, "request_id", None)
    user_id = identity["user"]["user_id"]
    conversation = None
    if payload.conversation_id:
        conversation = await conversation_repository.get_conversation(payload.conversation_id, user_id=user_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    if payload.session_id:
        session_conversation = await conversation_repository.get_session(payload.session_id, user_id=user_id)
        if session_conversation is None:
            raise HTTPException(status_code=404, detail="Conversation session not found.")
        conversation = session_conversation
    try:
        response_text, conversation_id = await ai_service.generate_response(payload.message, conversation_id=conversation.conversation_id if conversation else None, user_id=user_id, auth_session_id=identity["session"]["session_id"])
        saved = await conversation_repository.get_conversation(conversation_id, user_id=user_id)
        await record_audit(user_id, "conversation.message", "conversation", conversation_id)
        return ChatResponse(response=response_text, conversation_id=conversation_id, session_id=saved.session_id if saved else None, request_id=request_id)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat request failed request_id=%s", request_id)
        raise HTTPException(status_code=500, detail="The assistant is temporarily unavailable. Please try again.")


@router.post("/ai/chat/{conversation_id}", response_model=ChatResponse)
async def chat_with_conversation(conversation_id: str, payload: ChatRequest, request: Request, identity: dict = Depends(current_identity)):
    user_id = identity["user"]["user_id"]
    conversation = await conversation_repository.get_conversation(conversation_id, user_id=user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return await chat(payload.model_copy(update={"conversation_id": conversation_id, "session_id": None}), request, identity)


@router.get("/ai/conversations")
async def list_conversations(identity: dict = Depends(current_identity)):
    user_id = identity["user"]["user_id"]
    conversations = await conversation_repository.list_user_conversations(user_id)
    return {"user_id": user_id, "conversations": [{"conversation_id": item.conversation_id, "session_id": item.session_id, "auth_session_id": item.auth_session_id, "user_id": item.user_id, "updated_at": _iso(item.updated_at)} for item in conversations]}


@router.get("/ai/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str, identity: dict = Depends(current_identity)):
    conversation = await conversation_repository.get_conversation(conversation_id, user_id=identity["user"]["user_id"])
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"conversation_id": conversation.conversation_id, "session_id": conversation.session_id, "auth_session_id": conversation.auth_session_id, "user_id": conversation.user_id, "messages": [{"role": message.role, "content": message.content, "timestamp": _iso(message.timestamp)} for message in conversation.messages]}


@router.post("/customers", status_code=201)
async def create_customer(payload: CustomerCreate, identity: dict = Depends(current_identity)):
    record = await operations_repository.create_customer(identity["user"]["user_id"], payload.model_dump())
    await record_audit(identity["user"]["user_id"], "customer.create", "customer", record["customer_id"])
    return record


@router.get("/customers")
async def list_customers(identity: dict = Depends(current_identity)):
    return {"customers": await operations_repository.list_customers(identity["user"]["user_id"])}


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str, identity: dict = Depends(current_identity)):
    record = await operations_repository.get_customer(identity["user"]["user_id"], customer_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return record


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, payload: CustomerUpdate, identity: dict = Depends(current_identity)):
    record = await operations_repository.update_customer(identity["user"]["user_id"], customer_id, payload.model_dump(exclude_unset=True))
    if record is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    await record_audit(identity["user"]["user_id"], "customer.update", "customer", customer_id)
    return record


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str, identity: dict = Depends(current_identity)):
    if await operations_repository.delete_customer(identity["user"]["user_id"], customer_id):
        await record_audit(identity["user"]["user_id"], "customer.delete", "customer", customer_id)
        return {"status": "deleted"}
    if await operations_repository.get_customer(identity["user"]["user_id"], customer_id):
        raise HTTPException(status_code=409, detail="Customer has bookings and cannot be deleted.")
    raise HTTPException(status_code=404, detail="Customer not found.")


@router.post("/bookings", status_code=201)
async def create_booking(payload: BookingCreate, identity: dict = Depends(current_identity)):
    record = await operations_repository.create_booking(identity["user"]["user_id"], payload.model_dump())
    if record is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    await record_audit(identity["user"]["user_id"], "booking.create", "booking", record["booking_id"])
    return record


@router.get("/bookings")
async def list_bookings(customer_id: str | None = None, identity: dict = Depends(current_identity)):
    if customer_id and await operations_repository.get_customer(identity["user"]["user_id"], customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"bookings": await operations_repository.list_bookings(identity["user"]["user_id"], customer_id)}


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str, identity: dict = Depends(current_identity)):
    record = await operations_repository.get_booking(identity["user"]["user_id"], booking_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return record


@router.get("/customers/{customer_id}/bookings")
async def customer_bookings(customer_id: str, identity: dict = Depends(current_identity)):
    if await operations_repository.get_customer(identity["user"]["user_id"], customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"bookings": await operations_repository.list_bookings(identity["user"]["user_id"], customer_id)}


@router.post("/shipments", status_code=201)
async def create_shipment(payload: ShipmentCreate, identity: dict = Depends(current_identity)):
    record = await operations_repository.create_shipment(identity["user"]["user_id"], payload.model_dump())
    if record is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    await record_audit(identity["user"]["user_id"], "shipment.create", "shipment", record["shipment_id"])
    return record


@router.get("/shipments")
async def list_shipments(customer_id: str | None = None, identity: dict = Depends(current_identity)):
    if customer_id and await operations_repository.get_customer(identity["user"]["user_id"], customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"shipments": await operations_repository.list_shipments(identity["user"]["user_id"], customer_id)}


@router.get("/customers/{customer_id}/shipments")
async def customer_shipments(customer_id: str, identity: dict = Depends(current_identity)):
    if await operations_repository.get_customer(identity["user"]["user_id"], customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"shipments": await operations_repository.list_shipments(identity["user"]["user_id"], customer_id)}


@router.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: str, request: Request, identity: dict = Depends(current_identity)):
    normalized_id = shipment_id.strip().upper()
    if not normalized_id.startswith("SHP-") or len(normalized_id) < 8:
        raise HTTPException(status_code=400, detail="Invalid shipment ID format. Example: SHP-1001")
    shipment = await operations_repository.get_shipment(identity["user"]["user_id"], normalized_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail=f"Shipment '{normalized_id}' was not found.")
    return {"shipment_id": normalized_id, "status": "ok", "shipment": shipment, "request_id": getattr(request.state, "request_id", None)}
