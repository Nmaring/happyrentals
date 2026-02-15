from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _resolve_db_path() -> Path:
    # 1) explicit override
    env = os.getenv("DB_PATH")
    if env:
        p = Path(env)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # 2) running as PyInstaller EXE
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        data_dir = exe_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "happyrentals.db"

    # 3) dev: backend/happyrentals.db
    backend_dir = Path(__file__).resolve().parents[1]
    return backend_dir / "happyrentals.db"


DB_PATH = str(_resolve_db_path())
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print("DB_PATH =", DB_PATH)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
