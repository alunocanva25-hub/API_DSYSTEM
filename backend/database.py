from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import DATA_DIR

DEFAULT_SQLITE_URL = f"sqlite:///{DATA_DIR / 'ds_studio_go_v2.db'}"
RAW_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def normalize_database_url(url: str) -> str:
    if not url:
        return DEFAULT_SQLITE_URL

    # Compatibilidade com URLs antigas/postgres://
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg://" + url[len("postgresql://") :]

    return url


DATABASE_URL = normalize_database_url(RAW_DATABASE_URL)

engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
