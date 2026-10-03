import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.ai.service import ai_service
from app.api.models import ChatRequest, ChatResponse
from app.db.repositories.conversation_repository import conversation_repository, resolve_user_id
from app.db.repositories.shipment_repository import shipment_repository

logger = logging.getLogger("app.api.routes")
router = APIRouter()


@router.post(
    "/ai/chat",
    response_model=ChatResponse,
    responses={
        400: {"description": "Bad request"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def chat(request: ChatRequest, http_request: Request):
    request_id = getattr(http_request.state, "request_id", None)
    user_id = resolve_user_id(request.user_id)

    logger.info("chat request user_id=%s request_id=%s", user_id, request_id)

    try:
        response_text, conversation_id = await ai_service.generate_response(
            request.message,
            conversation_id=request.conversation_id,
            user_id=user_id,
        )
        return ChatResponse(
            response=response_text,
            status="ok",
            conversation_id=conversation_id,
            session_id=request.session_id or conversation_id,
            request_id=request_id,
        )
    except Exception:
        logger.exception("Chat request failed request_id=%s", request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The assistant is temporarily unavailable. Please try again.",
        )


@router.post(
    "/ai/chat/{conversation_id}",
    response_model=ChatResponse,
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Conversation not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def chat_with_conversation(conversation_id: str, request: ChatRequest, http_request: Request):
    request_id = getattr(http_request.state, "request_id", None)
    user_id = resolve_user_id(request.user_id)

    logger.info(
        "chat continue conversation_id=%s user_id=%s request_id=%s",
        conversation_id,
        user_id,
        request_id,
    )

    existing = await conversation_repository.get_conversation(conversation_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' was not found.",
        )

    try:
        response_text, resolved_conversation_id = await ai_service.generate_response(
            request.message,
            conversation_id=conversation_id,
            user_id=user_id,
        )
        return ChatResponse(
            response=response_text,
            status="ok",
            conversation_id=resolved_conversation_id,
            session_id=request.session_id or resolved_conversation_id,
            request_id=request_id,
        )
    except Exception:
        logger.exception("Chat continuation failed request_id=%s", request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The assistant is temporarily unavailable. Please try again.",
        )


@router.get("/ai/conversations")
async def list_conversations(user_id: str | None = None):
    resolved_user_id = resolve_user_id(user_id)
    conversations = await conversation_repository.list_user_conversations(resolved_user_id)
    return {
        "user_id": resolved_user_id,
        "conversations": [
            {
                "conversation_id": item.conversation_id,
                "session_id": item.session_id,
                "user_id": item.user_id,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in conversations
        ],
    }


@router.get("/ai/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    conversation = await conversation_repository.get_conversation(conversation_id)
    if conversation is None:
        return {"conversation_id": conversation_id, "messages": []}

    return {
        "conversation_id": conversation.conversation_id,
        "session_id": conversation.session_id,
        "user_id": conversation.user_id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
            }
            for message in conversation.messages
        ],
    }


@router.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: str, request: Request):
    request_id = getattr(request.state, "request_id", None)
    normalized_id = shipment_id.strip().upper()

    if not normalized_id:
        raise HTTPException(status_code=400, detail="Shipment ID is required.")

    if not normalized_id.startswith("SHP-") or len(normalized_id) < 8:
        raise HTTPException(
            status_code=400,
            detail="Invalid shipment ID format. Example: SHP-1001",
        )

    shipment = await shipment_repository.get_shipment(normalized_id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment '{normalized_id}' was not found.",
        )

    return {
        "shipment_id": normalized_id,
        "status": "ok",
        "shipment": shipment,
        "request_id": request_id,
    }
