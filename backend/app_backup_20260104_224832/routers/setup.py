import os
from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import text

from app.db import DB_URL, engine, SessionLocal
from app.models import User

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/ping")
def ping():
    return {"ok": True}


@router.get("/dbinfo")
def dbinfo():
    info = {
        "cwd": os.getcwd(),
        "db_url": DB_URL,
    }

    # Derive path from DB_URL for sqlite3 check
    db_path = DB_URL.replace("sqlite:///", "")
    info["db_path_from_db_url"] = db_path

    # File stats
    try:
        p = Path(db_path)
        info["db_file_exists"] = p.exists()
        info["db_file_size_bytes"] = p.stat().st_size if p.exists() else None
    except Exception as e:
        info["db_file_exists"] = False
        info["db_file_size_bytes"] = None
        info["db_file_error"] = str(e)

    # What SQLAlchemy engine is REALLY using
    try:
        with engine.connect() as conn:
            db_list = conn.execute(text("PRAGMA database_list")).fetchall()
            info["engine_pragma_database_list"] = [list(r) for r in db_list]
    except Exception as e:
        info["engine_pragma_database_list_error"] = str(e)

    # SQLAlchemy view of users
    try:
        db = SessionLocal()
        users = db.query(User.id, User.email).order_by(User.id).all()
        info["sqlalchemy_users"] = [[u[0], u[1]] for u in users]
        db.close()
    except Exception as e:
        info["sqlalchemy_users_error"] = str(e)

    # sqlite3 view of tables/users (from db_path_from_db_url)
    try:
        import sqlite3

        con = sqlite3.connect(db_path)
        tables = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        info["sqlite_tables"] = [list(t) for t in tables]

        sqlite_users = []
        if any(t[0] == "users" for t in tables):
            sqlite_users = con.execute(
                "SELECT id, email FROM users ORDER BY id"
            ).fetchall()
        info["sqlite_users"] = [list(u) for u in sqlite_users]
        con.close()
    except Exception as e:
        info["sqlite_error"] = str(e)

    return info
