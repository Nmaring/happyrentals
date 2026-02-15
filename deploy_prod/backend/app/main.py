# backend/app/main.py
import os
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.properties.router as properties_routes
import app.units.router as units_routes
import app.tenants.router as tenants_routes
import app.leases.router as leases_routes
import app.payments.router as payments_routes
import app.lease_builder.router as lease_builder_routes

from app.units.models import init_units_tables
from app.leases.models import init_leases_tables
from app.payments.models import init_payments_tables
from app.db_compat import engine

app = FastAPI(title="HappyRentals API")

api_router = APIRouter(prefix="/api")

FRONTEND_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup_init():
    # Force-create tables/columns (and ensure absolute DB path is used)
    init_units_tables()
    init_leases_tables()
    init_payments_tables()

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    # Always return JSON + CORS headers for easier browser debugging
    origin = request.headers.get("origin")
    headers = {"Vary": "Origin"}
    if origin in FRONTEND_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unhandled error: {type(exc).__name__}: {str(exc)}"},
        headers=headers,
    )
api_router.include_router(properties_routes.router)
api_router.include_router(units_routes.router)
api_router.include_router(tenants_routes.router)
api_router.include_router(leases_routes.router)
api_router.include_router(payments_routes.router)
api_router.include_router(lease_builder_routes.router)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/debug/db")
def debug_db():
    return {
        "engine_url": str(engine.url),
        "frontend_origin_env": os.getenv("FRONTEND_ORIGIN"),
        "allowed_origins": FRONTEND_ORIGINS,
    }


app.include_router(api_router)


# --- Added by packaging script ---
@app.get("/api/health", include_in_schema=False)
def api_health():
    return {"ok": True}

# --- Serve SPA (Vite build) ---
import os
from pathlib import Path
# --- DB auto-init (create tables if missing) ---
from app.db import Base, engine

@app.on_event("startup")
def _init_db():
    Base.metadata.create_all(bind=engine)

# --- Admin routes ---
from app.admin.router import router as admin_router
app.include_router(admin_router)

# --- SPA HISTORY FALLBACK ---
import os
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parents[1] / "static"))

if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    favicon = STATIC_DIR / "favicon.ico"
    if favicon.exists():
        @app.get("/favicon.ico", include_in_schema=False)
        def _favicon():
            return FileResponse(str(favicon))

    index_file = STATIC_DIR / "index.html"

    @app.get("/", include_in_schema=False)
    def _root():
        return FileResponse(str(index_file))

    @app.get("/{full_path:path}", include_in_schema=False)
    def _spa(full_path: str, request: Request):
        if request.url.path.startswith("/api/"):
            raise HTTPException(status_code=404)
        candidate = STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index_file))

