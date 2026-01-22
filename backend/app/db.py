import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DB_URL", "sqlite:///./happyrentals.db")

# SQLite needs check_same_thread=False for FastAPI threaded deps
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """
    Simple SQLite 'migration' helper:
    - create_all creates missing tables
    - but won't add columns to existing tables
    So we detect missing columns and ALTER TABLE ADD COLUMN.
    """
    if not DB_URL.startswith("sqlite"):
        return

    # table -> list of (column_name, sqlite_column_def)
    desired = {
        "units": [
            ("rent", "FLOAT"),
        ],
        # You can add more here later if needed, but keep it minimal.
    }

    with engine.connect() as conn:
        for table, cols in desired.items():
            # If table doesn't exist yet, skip (create_all will handle it)
            exists = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
                {"t": table},
            ).fetchone()
            if not exists:
                continue

            info = conn.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
            existing_cols = {row[1] for row in info}  # row[1] is column name

            for col_name, col_def in cols:
                if col_name in existing_cols:
                    continue
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"))
