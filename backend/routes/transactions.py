from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db, utcnow_naive
from backend.models.transaction import Transaction
from backend.schemas.transaction_schema import TransactionCreate, TransactionOut, TransactionUpdate
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master, require_master

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    include_deleted: bool = Query(default=False),
    kind: str | None = Query(default=None),
    category: str | None = Query(default=None),
    source: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[TransactionOut]:
    require_admin_or_master(current_user)

    stmt = select(Transaction)

    if not include_deleted:
        stmt = stmt.where(Transaction.deleted == False)  # noqa: E712
    if kind:
        stmt = stmt.where(Transaction.kind == kind)
    if category:
        stmt = stmt.where(Transaction.category == category)
    if source:
        stmt = stmt.where(Transaction.source == source)
    if date_from:
        stmt = stmt.where(Transaction.occurred_at >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.occurred_at <= date_to)

    items = db.scalars(stmt.order_by(Transaction.occurred_at.desc())).all()
    return [TransactionOut.model_validate(item) for item in items]


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TransactionOut:
    require_admin_or_master(current_user)

    if payload.kind not in {"entrada", "saida"}:
        raise HTTPException(status_code=400, detail="kind deve ser 'entrada' ou 'saida'.")

    item = Transaction(
        client_uid=payload.client_uid,
        external_id=payload.external_id,
        source=payload.source,
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


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TransactionOut:
    require_admin_or_master(current_user)

    item = db.get(Transaction, transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")

    data = payload.model_dump(exclude_unset=True)
    if "kind" in data and data["kind"] not in {"entrada", "saida"}:
        raise HTTPException(status_code=400, detail="kind deve ser 'entrada' ou 'saida'.")

    for key, value in data.items():
        setattr(item, key, value)

    if item.deleted and not item.deleted_at:
        item.deleted_at = utcnow_naive()
    if not item.deleted:
        item.deleted_at = None

    item.updated_by = current_user.username
    db.commit()
    db.refresh(item)
    return TransactionOut.model_validate(item)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_admin_or_master(current_user)

    item = db.get(Transaction, transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")

    if current_user.role == "master":
        db.delete(item)
        db.commit()
        return {"message": "Transação excluída definitivamente."}

    item.deleted = True
    item.deleted_at = utcnow_naive()
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Transação excluída logicamente."}


@router.post("/{transaction_id}/restore")
def restore_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_master(current_user)

    item = db.get(Transaction, transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")

    item.deleted = False
    item.deleted_at = None
    item.updated_by = current_user.username
    db.commit()
    return {"message": "Transação restaurada com sucesso."}
