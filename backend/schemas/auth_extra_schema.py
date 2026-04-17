from __future__ import annotations

from pydantic import BaseModel


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AppStatusResponse(BaseModel):
    app: str
    version: str
    status: str
    environment: str
    docs: str
    auth_mode: str
    desktop_integration_mode: str
    mobile_client_mode: str
