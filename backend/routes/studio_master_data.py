from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.models.professional import Professional
from backend.models.service import Service
from backend.schemas.master_data_schema import StudioMasterDataSyncPayload, StudioMasterDataSyncResponse
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio/master-data", tags=["Studio Master Data Sync"])


@router.post("/sync", response_model=StudioMasterDataSyncResponse)
def sync_studio_master_data(
    payload: StudioMasterDataSyncPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudioMasterDataSyncResponse:
    require_admin_or_master(current_user)

    clients_created = clients_updated = 0
    professionals_created = professionals_updated = 0
    services_created = services_updated = 0

    for item in payload.clients:
        conditions = []
        if item.external_id:
            conditions.append(Client.external_id == item.external_id)
        conditions.append(Client.name == item.name)
        existing = db.scalar(select(Client).where(or_(*conditions)))
        if not existing:
            existing = Client(
                external_id=item.external_id,
                source="desktop_sync",
                name=item.name,
                phone=item.phone,
                email=item.email,
                notes=item.notes,
                is_active=item.is_active,
                created_by=current_user.username,
                updated_by=current_user.username,
            )
            db.add(existing)
            clients_created += 1
        else:
            existing.external_id = item.external_id or existing.external_id
            existing.source = "desktop_sync"
            existing.name = item.name
            existing.phone = item.phone
            existing.email = item.email
            existing.notes = item.notes
            existing.is_active = item.is_active
            existing.updated_by = current_user.username
            clients_updated += 1

    for item in payload.professionals:
        conditions = []
        if item.external_id:
            conditions.append(Professional.external_id == item.external_id)
        conditions.append(Professional.name == item.name)
        existing = db.scalar(select(Professional).where(or_(*conditions)))
        if not existing:
            existing = Professional(
                external_id=item.external_id,
                source="desktop_sync",
                name=item.name,
                specialty=item.specialty,
                phone=item.phone,
                notes=item.notes,
                is_active=item.is_active,
                created_by=current_user.username,
                updated_by=current_user.username,
            )
            db.add(existing)
            professionals_created += 1
        else:
            existing.external_id = item.external_id or existing.external_id
            existing.source = "desktop_sync"
            existing.name = item.name
            existing.specialty = item.specialty
            existing.phone = item.phone
            existing.notes = item.notes
            existing.is_active = item.is_active
            existing.updated_by = current_user.username
            professionals_updated += 1

    for item in payload.services:
        conditions = []
        if item.external_id:
            conditions.append(Service.external_id == item.external_id)
        conditions.append(Service.name == item.name)
        existing = db.scalar(select(Service).where(or_(*conditions)))
        if not existing:
            existing = Service(
                external_id=item.external_id,
                source="desktop_sync",
                name=item.name,
                duration_minutes=item.duration_minutes,
                price=item.price,
                notes=item.notes,
                is_active=item.is_active,
                created_by=current_user.username,
                updated_by=current_user.username,
            )
            db.add(existing)
            services_created += 1
        else:
            existing.external_id = item.external_id or existing.external_id
            existing.source = "desktop_sync"
            existing.name = item.name
            existing.duration_minutes = item.duration_minutes
            existing.price = item.price
            existing.notes = item.notes
            existing.is_active = item.is_active
            existing.updated_by = current_user.username
            services_updated += 1

    db.commit()

    return StudioMasterDataSyncResponse(
        message="Bases mestre sincronizadas com sucesso.",
        source_system=payload.source_system,
        clients_received=len(payload.clients),
        clients_created=clients_created,
        clients_updated=clients_updated,
        professionals_received=len(payload.professionals),
        professionals_created=professionals_created,
        professionals_updated=professionals_updated,
        services_received=len(payload.services),
        services_created=services_created,
        services_updated=services_updated,
    )
