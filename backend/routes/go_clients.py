from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.schemas.go_client_schema import GoClientCreate
from backend.schemas.master_data_schema import ClientOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/go", tags=["GO Client Bridge"])


@router.post("/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_go_client(
    payload: GoClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ClientOut:
    require_admin_or_master(current_user)

    existing = None
    if payload.external_id:
        existing = db.scalar(select(Client).where(Client.external_id == payload.external_id))

    if existing:
        existing.name = payload.name
        existing.phone = payload.phone
        existing.email = payload.email
        existing.notes = payload.notes
        existing.is_active = payload.is_active
        existing.source = "go_mobile"
        existing.updated_by = current_user.username
        db.commit()
        db.refresh(existing)
        return ClientOut.model_validate(existing)

    item = Client(
        external_id=payload.external_id,
        source="go_mobile",
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        notes=payload.notes,
        is_active=payload.is_active,
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ClientOut.model_validate(item)
