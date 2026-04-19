from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StudioAppointmentItem(BaseModel):
    client_uid: str | None = None
    external_id: str | None = None
    client_name: str
    professional_name: str
    service_name: str
    phone: str | None = None
    notes: str | None = None
    start_at: datetime
    end_at: datetime
    deleted: bool = False


class StudioTransactionItem(BaseModel):
    client_uid: str | None = None
    external_id: str | None = None
    kind: str = Field(description="entrada ou saida")
    amount: float = Field(gt=0)
    category: str
    payment_method: str
    description: str | None = None
    occurred_at: datetime
    deleted: bool = False


class StudioDataSyncPayload(BaseModel):
    source_system: str = "DSYSTEM STUDIO"
    appointments: list[StudioAppointmentItem] = []
    transactions: list[StudioTransactionItem] = []


class StudioDataSyncResponse(BaseModel):
    message: str
    source_system: str
    appointments_received: int
    appointments_created: int
    appointments_updated: int
    appointments_ignored: int
    transactions_received: int
    transactions_created: int
    transactions_updated: int
    transactions_ignored: int
