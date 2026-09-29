from fastapi import FastAPI
from app.config.settings import settings
from pydantic import BaseModel
from app.ai.service import ai_service

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

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
    response = await ai_service.generate_response(request.message)

    return ChatResponse(response=response)