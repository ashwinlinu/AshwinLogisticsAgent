from typing import Any, Literal
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=128)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)
    # Identity comes exclusively from the authenticated session, never the payload.

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


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=256)
    full_name: str = Field(min_length=1, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("Enter a valid email address.")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if len(value.strip()) < 12:
            raise ValueError("Password must contain at least 12 non-whitespace characters.")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=160)
    industry: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    status: Literal["active", "inactive"] = "active"


class CustomerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=160)
    industry: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    status: Literal["active", "inactive"] | None = None


class BookingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str = Field(min_length=1, max_length=128)
    pickup_location: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    service_type: str = Field(min_length=1, max_length=120)
    status: str = "confirmed"


class ShipmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    booking_id: str = Field(min_length=1, max_length=128)
    status: str = "IN_TRANSIT"
    origin: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    carrier: str = Field(min_length=1, max_length=160)
    estimated_delivery: str | None = None
    last_update: str | None = None
