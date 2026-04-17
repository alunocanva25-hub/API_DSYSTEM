from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppointmentBase(BaseModel):
    client_uid: str | None = None
    client_name: str
    professional_name: str
    service_name: str
    phone: str | None = None
    notes: str | None = None
    start_at: datetime
    end_at: datetime


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    client_uid: str | None = None
    client_name: str | None = None
    professional_name: str | None = None
    service_name: str | None = None
    phone: str | None = None
    notes: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    deleted: bool | None = None


class AppointmentOut(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deleted: bool
    deleted_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime
