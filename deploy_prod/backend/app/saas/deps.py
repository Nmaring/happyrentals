from __future__ import annotations
from datetime import datetime
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.auth import decode_token

def _get_token(req: Request) -> str:
    # Prefer Authorization Bearer; fallback to cookie
    auth = req.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    c = req.cookies.get("hr_token", "")
    return (c or "").strip()

def get_current_user(req: Request, db: Session = Depends(get_db)) -> models.User:
    token = _get_token(req)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = int(payload.get("sub") or 0)
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def org_id(user: models.User = Depends(get_current_user)) -> int:
    return int(user.org_id)

def require_roles(user: models.User, roles: list[str]):
    if (user.role or "").lower() not in [r.lower() for r in roles]:
        raise HTTPException(status_code=403, detail="Forbidden")

def require_roles_dep(roles: list[str]):
    def _dep(user: models.User = Depends(get_current_user)):
        require_roles(user, roles)
        return True
    return _dep

def _get_sub(db: Session, oid: int) -> models.Subscription:
    sub = db.query(models.Subscription).filter(models.Subscription.org_id == oid).first()
    if not sub:
        sub = models.Subscription(org_id=oid, plan_type="per_unit", status="trialing")
        db.add(sub); db.commit(); db.refresh(sub)
    return sub

def require_subscription_read(db: Session = Depends(get_db), oid: int = Depends(org_id)):
    sub = _get_sub(db, oid)
    if (sub.status or "") in ("trialing", "active", "past_due"):
        return sub
    raise HTTPException(status_code=402, detail="Subscription required")

def require_subscription_write(db: Session = Depends(get_db), oid: int = Depends(org_id)):
    sub = _get_sub(db, oid)
    if (sub.status or "") in ("trialing", "active"):
        return sub
    raise HTTPException(status_code=402, detail="Subscription required (upgrade to continue)")
