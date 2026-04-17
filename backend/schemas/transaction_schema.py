from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    client_uid: str | None = None
    kind: str = Field(description="entrada ou saida")
    amount: float = Field(gt=0)
    category: str
    payment_method: str
    description: str | None = None
    occurred_at: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    client_uid: str | None = None
    kind: str | None = None
    amount: float | None = Field(default=None, gt=0)
    category: str | None = None
    payment_method: str | None = None
    description: str | None = None
    occurred_at: datetime | None = None
    deleted: bool | None = None


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deleted: bool
    deleted_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime
