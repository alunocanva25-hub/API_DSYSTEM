from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import APP_NAME, APP_VERSION
from backend.database import Base, SessionLocal, engine
from backend.models.user import User
from backend.routes.appointments import router as appointments_router
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router
from backend.routes.transactions import router as transactions_router
from backend.routes.users import router as users_router
from backend.utils.auth import hash_password

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="API V2.0.0.3 do DS STUDIO GO com JWT, Swagger Authorize corrigido, usuários, filtros e sync base.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(appointments_router)
app.include_router(transactions_router)
app.include_router(sync_router)


@app.get("/")
def root() -> dict:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "version": APP_VERSION}


def seed_default_master() -> None:
    db: Session = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.username == "master"))
        if existing:
            return

        user = User(
            username="master",
            password_hash=hash_password("123456"),
            full_name="Master DS Studio GO",
            role="master",
            is_active=True,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed_default_master()
