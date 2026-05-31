from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.schemas.master_data_schema import ClientOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio/pull", tags=["Studio Pull Clients"])


def _client_out(item: Client) -> ClientOut:
    deleted = not bool(item.is_active)
    return ClientOut(
        id=item.id,
        external_id=item.external_id,
        source=item.source,
        name=item.name,
        phone=item.phone,
        email=item.email,
        notes=item.notes,
        is_active=item.is_active,
        deleted=deleted,
        deleted_at=item.updated_at if deleted else None,
        created_by=item.created_by,
        updated_by=item.updated_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/clients", response_model=list[ClientOut])
def pull_go_clients(
    only_go_mobile: bool = Query(default=True),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ClientOut]:
    require_admin_or_master(current_user)
    stmt = select(Client)
    if only_go_mobile:
        stmt = stmt.where(Client.source == "go_mobile")
    if active_only:
        stmt = stmt.where(Client.is_active == True)  # noqa: E712
    items = db.scalars(stmt.order_by(Client.updated_at.asc())).all()
    return [_client_out(item) for item in items]
