from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.db import DB_PATH

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/db")
def db_info():
    p = Path(DB_PATH)
    return {
        "db_path": str(p),
        "exists": p.exists(),
        "size": p.stat().st_size if p.exists() else 0,
    }

@router.get("/backup")
def backup_db():
    p = Path(DB_PATH)
    if not p.exists():
        raise HTTPException(status_code=404, detail="DB file not found")
    # triggers browser download
    return FileResponse(
        str(p),
        filename=f"happyrentals_backup.db",
        media_type="application/octet-stream",
    )
