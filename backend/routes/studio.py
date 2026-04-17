from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.utils.auth import get_current_user
from backend.utils.permissions import require_admin_or_master

router = APIRouter(prefix="/api/studio", tags=["Studio Integration"])


class StudioPingResponse(BaseModel):
    message: str
    role: str
    source: str


class StudioSyncPayload(BaseModel):
    source_system: str = "DSYSTEM STUDIO"
    appointments: list[dict] = []
    transactions: list[dict] = []


@router.get("/ping", response_model=StudioPingResponse)
def studio_ping(current_user=Depends(get_current_user)) -> StudioPingResponse:
    require_admin_or_master(current_user)
    return StudioPingResponse(
        message="Integração Studio disponível.",
        role=current_user.role,
        source="API bridge",
    )


@router.post("/sync/full")
def studio_sync_full(
    payload: StudioSyncPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    require_admin_or_master(current_user)
    return {
        "message": "Payload do Studio recebido.",
        "source_system": payload.source_system,
        "received_appointments": len(payload.appointments),
        "received_transactions": len(payload.transactions),
        "integration_mode": "desktop_to_api_bridge",
    }
