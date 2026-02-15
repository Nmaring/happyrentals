from __future__ import annotations
﻿# backend/app/db_compat.py
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Always use an absolute DB path so cwd never changes which database you hit
BACKEND_DIR = Path(__file__).resolve().parents[1]  # ...\backend
DB_PATH = (BACKEND_DIR / "happyrentals.db").resolve()

# SQLAlchemy wants forward slashes for sqlite absolute paths on Windows
DB_URL = "sqlite:///" + str(DB_PATH).replace("\\", "/")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
