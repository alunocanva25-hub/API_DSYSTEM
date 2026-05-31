from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.desktop_sync_schema import (
    DesktopUsersSyncPayload,
    DesktopUsersSyncResponse,
)
from backend.utils.auth import get_current_user, hash_password
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio/users", tags=["Studio Users Sync"])


@router.post("/sync", response_model=DesktopUsersSyncResponse)
def sync_desktop_users(
    payload: DesktopUsersSyncPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> DesktopUsersSyncResponse:
    require_admin_or_master(current_user)

    created = 0
    updated = 0

    for item in payload.users:
        if item.role not in {"admin", "master"}:
            raise HTTPException(status_code=400, detail=f"Role inválido para usuário {item.username}.")

        user = None

        # Prioridade 1: external_id (regra principal para updates do desktop)
        if item.external_id:
            user = db.scalar(select(User).where(User.external_id == item.external_id))

        # Fallback: username atual enviado
        if not user:
            user = db.scalar(select(User).where(User.username == item.username))

        temp_password = item.temp_password or "123456"

        if not user:
            conflict = db.scalar(select(User).where(User.username == item.username))
            if conflict:
                raise HTTPException(status_code=400, detail=f"Username já existe na API: {item.username}")

            user = User(
                username=item.username,
                password_hash=hash_password(temp_password),
                full_name=item.full_name,
                role=item.role,
                is_active=item.is_active,
                source="desktop_sync",
                external_id=item.external_id,
                must_change_password=item.must_change_password,
            )
            db.add(user)
            created += 1
        else:
            # Se o username mudou no DSYSTEM STUDIO, sobrescrever na API
            if user.username != item.username:
                conflict = db.scalar(
                    select(User).where(
                        User.username == item.username,
                        User.id != user.id,
                    )
                )
                if conflict:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Não foi possível atualizar username para {item.username}: já existe outro usuário com esse login.",
                    )
                user.username = item.username

            user.full_name = item.full_name
            user.role = item.role
            user.is_active = item.is_active
            user.source = "desktop_sync"
            user.external_id = item.external_id
            user.must_change_password = item.must_change_password
            if item.temp_password:
                user.password_hash = hash_password(item.temp_password)
            updated += 1

    db.commit()

    return DesktopUsersSyncResponse(
        message="Usuários do desktop sincronizados com sucesso.",
        source_system=payload.source_system,
        received_users=len(payload.users),
        created_users=created,
        updated_users=updated,
    )
