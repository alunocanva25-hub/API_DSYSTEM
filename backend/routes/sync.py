from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.appointment import Appointment
from backend.models.transaction import Transaction
from backend.schemas.appointment_schema import AppointmentOut
from backend.schemas.transaction_schema import TransactionOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/sync", tags=["Sync"])


class SyncPushPayload(BaseModel):
    appointments: list[dict] = []
    transactions: list[dict] = []


class SyncPullResponse(BaseModel):
    appointments: list[AppointmentOut]
    transactions: list[TransactionOut]


@router.post("/push")
def sync_push(
    payload: SyncPushPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_admin_or_master(current_user)

    received_appointments = 0
    received_transactions = 0

    for raw in payload.appointments:
        client_uid = raw.get("client_uid")
        if not client_uid:
            continue

        item = db.scalar(select(Appointment).where(Appointment.client_uid == client_uid))
        if not item:
            item = Appointment(client_uid=client_uid)
            db.add(item)

        item.client_name = raw.get("client_name", item.client_name if getattr(item, "client_name", None) else "")
        item.professional_name = raw.get("professional_name", item.professional_name if getattr(item, "professional_name", None) else "")
        item.service_name = raw.get("service_name", item.service_name if getattr(item, "service_name", None) else "")
        item.phone = raw.get("phone")
        item.notes = raw.get("notes")
        item.start_at = datetime.fromisoformat(raw["start_at"])
        item.end_at = datetime.fromisoformat(raw["end_at"])
        item.deleted = bool(raw.get("deleted", False))
        item.created_by = item.created_by or current_user.username
        item.updated_by = current_user.username
        received_appointments += 1

    for raw in payload.transactions:
        client_uid = raw.get("client_uid")
        if not client_uid:
            continue

        item = db.scalar(select(Transaction).where(Transaction.client_uid == client_uid))
        if not item:
            item = Transaction(client_uid=client_uid)
            db.add(item)

        item.kind = raw["kind"]
        item.amount = float(raw["amount"])
        item.category = raw["category"]
        item.payment_method = raw["payment_method"]
        item.description = raw.get("description")
        item.occurred_at = datetime.fromisoformat(raw["occurred_at"])
        item.deleted = bool(raw.get("deleted", False))
        item.created_by = item.created_by or current_user.username
        item.updated_by = current_user.username
        received_transactions += 1

    db.commit()

    return {
        "message": "Sync push processado com sucesso.",
        "received_appointments": received_appointments,
        "received_transactions": received_transactions,
    }


@router.get("/pull", response_model=SyncPullResponse)
def sync_pull(
    since: datetime,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> SyncPullResponse:
    require_admin_or_master(current_user)

    appointments = db.scalars(
        select(Appointment).where(
            or_(Appointment.created_at >= since, Appointment.updated_at >= since)
        ).order_by(Appointment.updated_at.asc())
    ).all()

    transactions = db.scalars(
        select(Transaction).where(
            or_(Transaction.created_at >= since, Transaction.updated_at >= since)
        ).order_by(Transaction.updated_at.asc())
    ).all()

    return SyncPullResponse(
        appointments=[AppointmentOut.model_validate(item) for item in appointments],
        transactions=[TransactionOut.model_validate(item) for item in transactions],
    )
