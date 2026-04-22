from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.models.professional import Professional
from backend.models.service import Service
from backend.schemas.master_data_schema import ClientOut, ProfessionalOut, ServiceOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api", tags=["Master Data"])


@router.get("/clients", response_model=list[ClientOut])
def list_clients(
    source: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ClientOut]:
    require_admin_or_master(current_user)
    stmt = select(Client)
    if source:
        stmt = stmt.where(Client.source == source)
    if active_only:
        stmt = stmt.where(Client.is_active == True)  # noqa: E712
    items = db.scalars(stmt.order_by(Client.name.asc())).all()
    return [ClientOut.model_validate(item) for item in items]


@router.get("/professionals", response_model=list[ProfessionalOut])
def list_professionals(
    source: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ProfessionalOut]:
    require_admin_or_master(current_user)
    stmt = select(Professional)
    if source:
        stmt = stmt.where(Professional.source == source)
    if active_only:
        stmt = stmt.where(Professional.is_active == True)  # noqa: E712
    items = db.scalars(stmt.order_by(Professional.name.asc())).all()
    return [ProfessionalOut.model_validate(item) for item in items]


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    source: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ServiceOut]:
    require_admin_or_master(current_user)
    stmt = select(Service)
    if source:
        stmt = stmt.where(Service.source == source)
    if active_only:
        stmt = stmt.where(Service.is_active == True)  # noqa: E712
    items = db.scalars(stmt.order_by(Service.name.asc())).all()
    return [ServiceOut.model_validate(item) for item in items]
