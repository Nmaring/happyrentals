# backend/app/debug/router.py
import os
from fastapi import APIRouter

try:
    from app.db import engine  # type: ignore
except Exception:
    engine = None  # type: ignore

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/db")
def debug_db():
    url = None
    try:
        if engine is not None:
            url = str(engine.url)
    except Exception:
        url = None

    return {
        "cwd": os.getcwd(),
        "engine_url": url,
        "frontend_origin_env": os.getenv("FRONTEND_ORIGIN"),
    }
