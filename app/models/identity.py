from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str
    email: str
    password_hash: str
    full_name: str
    role: Literal["admin", "operator", "support"]
    status: Literal["active", "disabled"]
    created_at: datetime
    updated_at: datetime


class SessionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str
    user_id: str
    token_hash: str
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    is_active: bool
