from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=128)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)
    user_id: str = Field(default="ashwinlinu", min_length=1, max_length=128)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message cannot be empty")
        return cleaned


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response: str
    status: str = "ok"
    conversation_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    shipment_id: str
    status: str = "ok"
    shipment: dict[str, Any]
    request_id: str | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    message: str
    status_code: int
    request_id: str | None = None
