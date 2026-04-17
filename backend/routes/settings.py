from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import APP_NAME, APP_VERSION
from backend.database import get_db
from backend.models.user import User
from backend.schemas.auth_extra_schema import AppStatusResponse, ChangePasswordRequest
from backend.schemas.user_schema import UserOut
from backend.utils.auth import get_current_user, hash_password, verify_password
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api", tags=["Settings"])


@router.get("/status", response_model=AppStatusResponse)
def app_status() -> AppStatusResponse:
    return AppStatusResponse(
        app=APP_NAME,
        version=APP_VERSION,
        status="ok",
        environment="production_or_local",
        docs="/docs",
        auth_mode="JWT Bearer",
        desktop_integration_mode="DSYSTEM STUDIO desktop = sistema principal",
        mobile_client_mode="DS STUDIO GO = cliente mobile da API",
    )


@router.post("/change-password", response_model=UserOut)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UserOut:
    require_admin_or_master(current_user)

    user = db.get(User, current_user.id)

    if not verify_password(payload.current_password, user.password_hash):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual inválida.",
        )

    if len(payload.new_password) < 6:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ter pelo menos 6 caracteres.",
        )

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
