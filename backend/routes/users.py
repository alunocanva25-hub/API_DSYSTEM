from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user_schema import UserCreate, UserOut, UserUpdate
from backend.utils.auth import get_current_user, hash_password
from backend.utils.permissions import require_master

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[UserOut]:
    require_master(current_user)
    items = db.scalars(select(User).order_by(User.username.asc())).all()
    return [UserOut.model_validate(item) for item in items]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UserOut:
    require_master(current_user)

    if payload.role not in {"admin", "master"}:
        raise HTTPException(status_code=400, detail="role deve ser admin ou master.")

    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists:
        raise HTTPException(status_code=400, detail="username já existe.")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active,
        source=payload.source,
        external_id=payload.external_id,
        must_change_password=payload.must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UserOut:
    require_master(current_user)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    data = payload.model_dump(exclude_unset=True)

    if "role" in data and data["role"] not in {"admin", "master"}:
        raise HTTPException(status_code=400, detail="role deve ser admin ou master.")

    if "password" in data and data["password"]:
        user.password_hash = hash_password(data.pop("password"))

    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
