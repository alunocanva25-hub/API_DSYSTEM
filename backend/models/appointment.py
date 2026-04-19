from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base, utcnow_naive


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_uid: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="api_local", index=True)
    client_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    professional_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    end_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=utcnow_naive, onupdate=utcnow_naive, nullable=False)
