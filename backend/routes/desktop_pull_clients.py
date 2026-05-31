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
    return [ClientOut.model_validate(item) for item in items]
