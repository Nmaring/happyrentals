from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.saas.db import Base, engine
from app.saas.deps import require_roles_dep

from app.saas.routers.auth_router import router as auth_router
from app.saas.routers.billing_router import router as billing_router
from app.saas.routers.invite_router import router as invite_router
from app.saas.routers.maintenance_router import router as maintenance_router

from app.saas.routers.properties_router import router as properties_router
from app.saas.routers.units_router import router as units_router
from app.saas.routers.tenants_router import router as tenants_router
from app.saas.routers.leases_router import router as leases_router
from app.saas.routers.payments_router import router as payments_router

app = FastAPI(title="HappyRentals SaaS")

@app.get("/api/health", include_in_schema=False)
def health():
    return {"ok": True}

@app.on_event("startup")
def _init_db():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public-ish auth routes
app.include_router(auth_router)
app.include_router(invite_router)       # accept invite is public; create invite is role-gated
app.include_router(billing_router)      # role-gated inside router
app.include_router(maintenance_router)  # tenant-safe inside router

# Landlord resources: owner/manager only
_owner_mgr = [Depends(require_roles_dep(["owner","manager"]))]

app.include_router(properties_router, dependencies=_owner_mgr)
app.include_router(units_router, dependencies=_owner_mgr)
app.include_router(tenants_router, dependencies=_owner_mgr)
app.include_router(leases_router, dependencies=_owner_mgr)
app.include_router(payments_router, dependencies=_owner_mgr)

# Static SPA
static_path = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parents[1] / "static"))
assets_dir = static_path / "assets"
index_file = static_path / "index.html"
favicon = static_path / "favicon.ico"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/favicon.ico", include_in_schema=False)
def _favicon():
    if favicon.exists():
        return FileResponse(str(favicon))
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.get("/", include_in_schema=False)
def _root():
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(status_code=500, content={"detail":"UI not built (missing static/index.html)"})

@app.get("/{path:path}", include_in_schema=False)
def _spa(path: str):
    if path.startswith("api/") or path.startswith("api"):
        return JSONResponse(status_code=404, content={"detail":"Not found"})
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(status_code=500, content={"detail":"UI not built (missing static/index.html)"})
