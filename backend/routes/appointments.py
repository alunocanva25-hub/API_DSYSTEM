from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db, utcnow_naive
from backend.models.appointment import Appointment
from backend.schemas.appointment_schema import AppointmentCreate, AppointmentOut, AppointmentUpdate
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master, require_master

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    include_deleted: bool = Query(default=False),
    professional_name: str | None = Query(default=None),
    source: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[AppointmentOut]:
    require_admin_or_master(current_user)

    stmt = select(Appointment)

    if not include_deleted:
        stmt = stmt.where(Appointment.deleted == False)  # noqa: E712
    if professional_name:
        stmt = stmt.where(Appointment.professional_name == professional_name)
    if source:
        stmt = stmt.where(Appointment.source == source)
    if date_from:
        stmt = stmt.where(Appointment.start_at >= date_from)
    if date_to:
        stmt = stmt.where(Appointment.start_at <= date_to)

    items = db.scalars(stmt.order_by(Appointment.start_at.asc())).all()
    return [AppointmentOut.model_validate(item) for item in items]


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AppointmentOut:
    require_admin_or_master(current_user)

    if payload.end_at <= payload.start_at:
        raise HTTPException(status_code=400, detail="end_at deve ser maior que start_at.")

    item = Appointment(
        client_uid=payload.client_uid,
        external_id=payload.external_id,
        source=payload.source,
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


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AppointmentOut:
    require_admin_or_master(current_user)

    item = db.get(Appointment, appointment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)

    if item.end_at <= item.start_at:
        raise HTTPException(status_code=400, detail="end_at deve ser maior que start_at.")

    if item.deleted and not item.deleted_at:
        item.deleted_at = utcnow_naive()
    if not item.deleted:
        item.deleted_at = None

    item.updated_by = current_user.username
    db.commit()
    db.refresh(item)
    return AppointmentOut.model_validate(item)


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_admin_or_master(current_user)

    item = db.get(Appointment, appointment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    if current_user.role == "master":
        db.delete(item)
        db.commit()
        return {"message": "Agendamento excluído definitivamente."}

    item.deleted = True
    item.deleted_at = utcnow_naive()
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Agendamento excluído logicamente."}


@router.post("/{appointment_id}/restore")
def restore_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_master(current_user)

    item = db.get(Appointment, appointment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    item.deleted = False
    item.deleted_at = None
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Agendamento restaurado com sucesso."}
