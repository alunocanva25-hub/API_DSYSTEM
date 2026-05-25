from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.appointment import Appointment
from backend.models.transaction import Transaction
from backend.schemas.appointment_schema import AppointmentOut
from backend.schemas.transaction_schema import TransactionOut
from backend.schemas.go_write_schema import GoAppointmentCreate, GoTransactionCreate
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/go", tags=["GO Write Bridge"])


@router.post("/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_go_appointment(
    payload: GoAppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AppointmentOut:
    require_admin_or_master(current_user)

    if payload.end_at <= payload.start_at:
        raise HTTPException(status_code=400, detail="end_at deve ser maior que start_at.")

    conditions = []
    if payload.external_id:
        conditions.append(Appointment.external_id == payload.external_id)
    if payload.client_uid:
        conditions.append(Appointment.client_uid == payload.client_uid)

    existing = None
    if conditions:
        existing = db.scalar(select(Appointment).where(or_(*conditions)))

    if existing:
        existing.client_uid = payload.client_uid or existing.client_uid
        existing.external_id = payload.external_id or existing.external_id
        existing.source = "go_mobile"
        existing.last_source = "go_mobile"
        existing.sync_status = "updated"
        existing.client_name = payload.client_name
        existing.professional_name = payload.professional_name
        existing.service_name = payload.service_name
        existing.phone = payload.phone
        existing.notes = payload.notes
        existing.start_at = payload.start_at
        existing.end_at = payload.end_at
        existing.deleted = False
        existing.deleted_at = None
        existing.updated_by = current_user.username
        db.commit()
        db.refresh(existing)
        return AppointmentOut.model_validate(existing)

    item = Appointment(
        client_uid=payload.client_uid,
        external_id=payload.external_id,
        source="go_mobile",
        last_source="go_mobile",
        sync_status="created",
        client_name=payload.client_name,
        professional_name=payload.professional_name,
        service_name=payload.service_name,
        phone=payload.phone,
        notes=payload.notes,
        start_at=payload.start_at,
        end_at=payload.end_at,
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return AppointmentOut.model_validate(item)


@router.post("/transactions", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_go_transaction(
    payload: GoTransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TransactionOut:
    require_admin_or_master(current_user)

    if payload.kind not in {"entrada", "saida"}:
        raise HTTPException(status_code=400, detail="kind deve ser 'entrada' ou 'saida'.")

    conditions = []
    if payload.external_id:
        conditions.append(Transaction.external_id == payload.external_id)
    if payload.client_uid:
        conditions.append(Transaction.client_uid == payload.client_uid)

    existing = None
    if conditions:
        existing = db.scalar(select(Transaction).where(or_(*conditions)))

    if existing:
        existing.client_uid = payload.client_uid or existing.client_uid
        existing.external_id = payload.external_id or existing.external_id
        existing.source = "go_mobile"
        existing.last_source = "go_mobile"
        existing.sync_status = "updated"
        existing.kind = payload.kind
        existing.amount = payload.amount
        existing.category = payload.category
        existing.payment_method = payload.payment_method
        existing.description = payload.description
        existing.occurred_at = payload.occurred_at
        existing.deleted = False
        existing.deleted_at = None
        existing.updated_by = current_user.username
        db.commit()
        db.refresh(existing)
        return TransactionOut.model_validate(existing)

    item = Transaction(
        client_uid=payload.client_uid,
        external_id=payload.external_id,
        source="go_mobile",
        last_source="go_mobile",
        sync_status="created",
        kind=payload.kind,
        amount=payload.amount,
        category=payload.category,
        payment_method=payload.payment_method,
        description=payload.description,
        occurred_at=payload.occurred_at,
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return TransactionOut.model_validate(item)
