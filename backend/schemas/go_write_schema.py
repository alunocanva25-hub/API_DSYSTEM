from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class GoAppointmentCreate(BaseModel):
    client_uid: str | None = None
    external_id: str | None = None
    client_name: str
    professional_name: str
    service_name: str
    phone: str | None = None
    notes: str | None = None
    start_at: datetime
    end_at: datetime


class GoTransactionCreate(BaseModel):
    client_uid: str | None = None
    external_id: str | None = None
    kind: str = Field(description="entrada ou saida")
    amount: float = Field(gt=0)
    category: str
    payment_method: str
    description: str | None = None
    occurred_at: datetime
