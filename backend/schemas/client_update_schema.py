from __future__ import annotations

from pydantic import BaseModel


class ClientUpdate(BaseModel):
    external_id: str | None = None
    source: str | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool | None = None
