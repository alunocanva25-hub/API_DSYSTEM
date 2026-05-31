from __future__ import annotations

from pydantic import BaseModel


class GoClientCreate(BaseModel):
    external_id: str | None = None
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool = True
