from __future__ import annotations

from pydantic import BaseModel


class DesktopUserItem(BaseModel):
    username: str
    full_name: str
    role: str = "admin"
    is_active: bool = True
    external_id: str | None = None
    temp_password: str | None = None
    must_change_password: bool = True


class DesktopUsersSyncPayload(BaseModel):
    source_system: str = "DSYSTEM STUDIO"
    users: list[DesktopUserItem]


class DesktopUsersSyncResponse(BaseModel):
    message: str
    source_system: str
    received_users: int
    created_users: int
    updated_users: int
