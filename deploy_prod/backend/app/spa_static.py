from __future__ import annotations

import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles


def mount_spa(app) -> None:
    \"\"\"Mount SPA static assets with HTML fallback, and provide /api/health.\"\"\"

    @app.get("/api/health")
    def health():
        return {"ok": True}

    static_dir = os.getenv("STATIC_DIR")
    if static_dir:
        static_path = Path(static_dir)
    else:
        # backend/app/... -> backend/static
        static_path = Path(__file__).resolve().parents[1] / "static"

    if static_path.exists():
        # IMPORTANT: mount after /api routes are registered in main.py
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
