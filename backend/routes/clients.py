from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.client import Client
from backend.schemas.client_update_schema import ClientUpdate
from backend.schemas.master_data_schema import ClientOut
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master, require_master

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("", response_model=list[ClientOut])
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


def _apply_client_update(client_id: int, payload: ClientUpdate, db: Session, current_user) -> ClientOut:
    require_admin_or_master(current_user)
    item = db.get(Client, client_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)

    item.updated_by = current_user.username
    db.commit()
    db.refresh(item)
    return ClientOut.model_validate(item)


@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ClientOut:
    return _apply_client_update(client_id, payload, db, current_user)


@router.patch("/{client_id}", response_model=ClientOut)
def patch_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ClientOut:
    return _apply_client_update(client_id, payload, db, current_user)


@router.delete("/{client_id}")
def deactivate_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_admin_or_master(current_user)
    item = db.get(Client, client_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    item.is_active = False
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Cliente inativado com sucesso."}


@router.post("/{client_id}/restore")
def restore_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_master(current_user)
    item = db.get(Client, client_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    item.is_active = True
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Cliente reativado com sucesso."}
