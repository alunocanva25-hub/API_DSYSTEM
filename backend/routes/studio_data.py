from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database import get_db, utcnow_naive
from backend.models.appointment import Appointment
from backend.models.transaction import Transaction
from backend.schemas.desktop_data_sync_schema import StudioDataSyncPayload, StudioDataSyncResponse
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio/data", tags=["Studio Data Sync"])


@router.post("/sync", response_model=StudioDataSyncResponse)
def sync_studio_data(
    payload: StudioDataSyncPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudioDataSyncResponse:
    require_admin_or_master(current_user)

    appt_created = 0
    appt_updated = 0
    appt_ignored = 0

    txn_created = 0
    txn_updated = 0
    txn_ignored = 0

    for item in payload.appointments:
        if item.end_at <= item.start_at:
            appt_ignored += 1
            continue

        existing = None
        conditions = []
        if item.client_uid:
            conditions.append(Appointment.client_uid == item.client_uid)
        if item.external_id:
            conditions.append(Appointment.external_id == item.external_id)

        if conditions:
            existing = db.scalar(select(Appointment).where(or_(*conditions)))

        if not existing and not item.client_uid and not item.external_id:
            appt_ignored += 1
            continue

        if not existing:
            existing = Appointment(
                client_uid=item.client_uid,
                external_id=item.external_id,
                source="desktop_sync",
                client_name=item.client_name,
                professional_name=item.professional_name,
                service_name=item.service_name,
                phone=item.phone,
                notes=item.notes,
                start_at=item.start_at,
                end_at=item.end_at,
                deleted=item.deleted,
                deleted_at=utcnow_naive() if item.deleted else None,
                created_by=current_user.username,
                updated_by=current_user.username,
            )
            db.add(existing)
            appt_created += 1
        else:
            existing.client_uid = item.client_uid or existing.client_uid
            existing.external_id = item.external_id or existing.external_id
            existing.source = "desktop_sync"
            existing.client_name = item.client_name
            existing.professional_name = item.professional_name
            existing.service_name = item.service_name
            existing.phone = item.phone
            existing.notes = item.notes
            existing.start_at = item.start_at
            existing.end_at = item.end_at
            existing.deleted = item.deleted
            existing.deleted_at = utcnow_naive() if item.deleted else None
            existing.updated_by = current_user.username
            appt_updated += 1

    for item in payload.transactions:
        if item.kind not in {"entrada", "saida"}:
            txn_ignored += 1
            continue

        existing = None
        conditions = []
        if item.client_uid:
            conditions.append(Transaction.client_uid == item.client_uid)
        if item.external_id:
            conditions.append(Transaction.external_id == item.external_id)

        if conditions:
            existing = db.scalar(select(Transaction).where(or_(*conditions)))

        if not existing and not item.client_uid and not item.external_id:
            txn_ignored += 1
            continue

        if not existing:
            existing = Transaction(
                client_uid=item.client_uid,
                external_id=item.external_id,
                source="desktop_sync",
                kind=item.kind,
                amount=item.amount,
                category=item.category,
                payment_method=item.payment_method,
                description=item.description,
                occurred_at=item.occurred_at,
                deleted=item.deleted,
                deleted_at=utcnow_naive() if item.deleted else None,
                created_by=current_user.username,
                updated_by=current_user.username,
            )
            db.add(existing)
            txn_created += 1
        else:
            existing.client_uid = item.client_uid or existing.client_uid
            existing.external_id = item.external_id or existing.external_id
            existing.source = "desktop_sync"
            existing.kind = item.kind
            existing.amount = item.amount
            existing.category = item.category
            existing.payment_method = item.payment_method
            existing.description = item.description
            existing.occurred_at = item.occurred_at
            existing.deleted = item.deleted
            existing.deleted_at = utcnow_naive() if item.deleted else None
            existing.updated_by = current_user.username
            txn_updated += 1

    db.commit()

    return StudioDataSyncResponse(
        message="Dados do Studio sincronizados com sucesso.",
        source_system=payload.source_system,
        appointments_received=len(payload.appointments),
        appointments_created=appt_created,
        appointments_updated=appt_updated,
        appointments_ignored=appt_ignored,
        transactions_received=len(payload.transactions),
        transactions_created=txn_created,
        transactions_updated=txn_updated,
        transactions_ignored=txn_ignored,
    )
