from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.appointment import Appointment
from backend.models.transaction import Transaction
from backend.schemas.appointment_schema import AppointmentOut
from backend.schemas.transaction_schema import TransactionOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio/pull", tags=["Studio Pull Bridge"])


@router.get("/appointments", response_model=list[AppointmentOut])
def pull_go_appointments(
    since: datetime | None = Query(default=None),
    only_go_mobile: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[AppointmentOut]:
    require_admin_or_master(current_user)
    stmt = select(Appointment)
    if only_go_mobile:
        stmt = stmt.where(Appointment.source == "go_mobile")
    if since:
        stmt = stmt.where(Appointment.updated_at >= since)
    items = db.scalars(stmt.order_by(Appointment.updated_at.asc())).all()
    return [AppointmentOut.model_validate(item) for item in items]


@router.get("/transactions", response_model=list[TransactionOut])
def pull_go_transactions(
    since: datetime | None = Query(default=None),
    only_go_mobile: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[TransactionOut]:
    require_admin_or_master(current_user)
    stmt = select(Transaction)
    if only_go_mobile:
        stmt = stmt.where(Transaction.source == "go_mobile")
    if since:
        stmt = stmt.where(Transaction.updated_at >= since)
    items = db.scalars(stmt.order_by(Transaction.updated_at.asc())).all()
    return [TransactionOut.model_validate(item) for item in items]
