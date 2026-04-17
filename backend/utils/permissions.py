from __future__ import annotations

from fastapi import HTTPException, status

from backend.utils.auth import CurrentUser


def require_admin_or_master(user: CurrentUser) -> None:
    if user.role not in {"admin", "master"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente.",
        )


def require_master(user: CurrentUser) -> None:
    if user.role != "master":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas master pode executar esta ação.",
        )
