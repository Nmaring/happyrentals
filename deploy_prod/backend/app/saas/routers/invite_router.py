from __future__ import annotations
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.auth import hash_password
from app.saas.deps import get_current_user, org_id, require_roles, require_subscription_write

router = APIRouter(prefix="/api/invites", tags=["invites"])
INVITE_TTL_HOURS = 72

class InviteCreateIn(BaseModel):
    email: EmailStr

class InviteAcceptIn(BaseModel):
    token: str
    password: str

@router.post("")
def create_invite(
    payload: InviteCreateIn,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _sub=Depends(require_subscription_write),
):
    require_roles(user, ["owner", "manager"])

    email = str(payload.email).lower().strip()
    existing = db.query(models.User).filter(models.User.org_id == oid, models.User.email == email).first()

    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=INVITE_TTL_HOURS)

    if not existing:
        existing = models.User(
            org_id=oid,
            email=email,
            role="tenant",
            hashed_password=hash_password(secrets.token_urlsafe(18)),
            is_active=False,
        )
        db.add(existing); db.commit(); db.refresh(existing)

    existing.invite_token = token
    existing.invite_expires_at = expires
    existing.role = "tenant"
    existing.is_active = False
    db.commit()

    return {"invite_url": f"/accept-invite?token={token}", "email": email}

@router.post("/accept")
def accept_invite(payload: InviteAcceptIn, db: Session = Depends(get_db)):
    token = (payload.token or "").strip()
    if not token:
        raise HTTPException(status_code=422, detail="token required")
    if not payload.password or len(payload.password) < 8:
        raise HTTPException(status_code=422, detail="password must be at least 8 characters")

    u = db.query(models.User).filter(models.User.invite_token == token).first()
    if not u:
        raise HTTPException(status_code=404, detail="Invalid invite token")
    if u.invite_expires_at and u.invite_expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Invite expired")

    u.hashed_password = hash_password(payload.password)
    u.is_active = True
    u.invite_token = None
    u.invite_expires_at = None
    db.commit()
    return {"ok": True, "email": u.email}
