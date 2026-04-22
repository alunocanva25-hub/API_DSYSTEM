from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str | None = None
    source: str
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ProfessionalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str | None = None
    source: str
    name: str
    specialty: str | None = None
    phone: str | None = None
    notes: str | None = None
    is_active: bool
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str | None = None
    source: str
    name: str
    duration_minutes: int
    price: float
    notes: str | None = None
    is_active: bool
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime


class StudioClientItem(BaseModel):
    external_id: str | None = None
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool = True


class StudioProfessionalItem(BaseModel):
    external_id: str | None = None
    name: str
    specialty: str | None = None
    phone: str | None = None
    notes: str | None = None
    is_active: bool = True


class StudioServiceItem(BaseModel):
    external_id: str | None = None
    name: str
    duration_minutes: int = Field(default=60, ge=1)
    price: float = Field(default=0, ge=0)
    notes: str | None = None
    is_active: bool = True


class StudioMasterDataSyncPayload(BaseModel):
    source_system: str = "DSYSTEM STUDIO"
    clients: list[StudioClientItem] = []
    professionals: list[StudioProfessionalItem] = []
    services: list[StudioServiceItem] = []


class StudioMasterDataSyncResponse(BaseModel):
    message: str
    source_system: str
    clients_received: int
    clients_created: int
    clients_updated: int
    professionals_received: int
    professionals_created: int
    professionals_updated: int
    services_received: int
    services_created: int
    services_updated: int
