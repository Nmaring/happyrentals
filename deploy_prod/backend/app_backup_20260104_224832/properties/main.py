# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import models so SQLAlchemy is aware of them (helpful if you use create_all)
from app.properties import models as _properties_models  # noqa: F401
import app.properties.router as properties_routes


app = FastAPI(title="HappyRentals API")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties_routes.router)

# (Keep your existing routers here if you have them)
# app.include_router(...)

@app.get("/health")
def health():
    return {"ok": True}
