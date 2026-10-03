from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.service import ai_service
from app.config.settings import settings
from app.db.repositories.conversation_repository import conversation_repository, resolve_user_id


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    status: str = "ok"
    conversation_id: str | None = None
    session_id: str | None = None


class ConversationListItem(BaseModel):
    conversation_id: str
    user_id: str | None = None
    updated_at: str | None = None


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
    }


@app.post("/ai/chat")
async def chat(request: ChatRequest):
    try:
        response, conversation_id = await ai_service.generate_response(
            request.message,
            conversation_id=request.conversation_id,
            session_id=request.session_id,
            user_id=request.user_id,
        )
        return ChatResponse(
            response=response,
            status="ok",
            conversation_id=conversation_id,
            session_id=request.session_id or conversation_id,
        )
    except Exception:
        return ChatResponse(
            response="The assistant is temporarily unavailable. Please try again.",
            status="error",
            conversation_id=request.conversation_id,
            session_id=request.session_id,
        )


@app.get("/ai/conversations")
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


@app.get("/ai/conversations/{conversation_id}/history")
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