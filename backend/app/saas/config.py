from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    APP_MODE: str = os.getenv("APP_MODE", "local")  # local | saas
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./saas.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    JWT_EXPIRE_MIN: int = int(os.getenv("JWT_EXPIRE_MIN", "43200"))  # 30 days

    # Stripe (SaaS only)
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_PER_UNIT: str = os.getenv("STRIPE_PRICE_PER_UNIT", "")
    STRIPE_PRICE_PER_TENANT: str = os.getenv("STRIPE_PRICE_PER_TENANT", "")
    STRIPE_SUCCESS_URL: str = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:5173/app?billing=success")
    STRIPE_CANCEL_URL: str = os.getenv("STRIPE_CANCEL_URL", "http://localhost:5173/app?billing=cancel")
    STRIPE_PORTAL_RETURN_URL: str = os.getenv("STRIPE_PORTAL_RETURN_URL", "http://localhost:5173/app/billing")

settings = Settings()
