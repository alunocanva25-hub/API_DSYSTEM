from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "admin"
    is_active: bool = True
    source: str = "api_local"
    external_id: str | None = None
    must_change_password: bool = False


class UserUpdate(BaseModel):
    password: str | None = None
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    source: str | None = None
    external_id: str | None = None
    must_change_password: bool | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
    source: str
    external_id: str | None = None
    must_change_password: bool
    created_at: datetime
    updated_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserOut
