from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "DS STUDIO GO API"
APP_VERSION = "2.0.0.5"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

JWT_SECRET = os.getenv("JWT_SECRET", "ds_studio_go_change_this_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 12
