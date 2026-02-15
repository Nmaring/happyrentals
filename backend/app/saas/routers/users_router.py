from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.auth import hash_password
from app.saas.deps import org_id, require_roles, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/users", tags=["users"])

class UserOut(BaseModel):
    id: int
    org_id: int
    email: str
    role: str
    is_active: bool
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "manager"  # owner|manager|staff|tenant

class InviteTenantIn(BaseModel):
    tenant_id: int
    email: EmailStr
    password: str

@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    _sub=Depends(require_subscription_read),
    _role=Depends(require_roles("owner", "manager")),
):
    return db.query(models.User).filter(models.User.org_id == oid).order_by(models.User.id.asc()).all()

@router.post("", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    _sub=Depends(require_subscription_write),
    _role=Depends(require_roles("owner")),
):
    email = str(payload.email).lower().strip()
    if payload.role not in ("owner", "manager", "staff", "tenant"):
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = models.User(
        org_id=oid,
        email=email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/invite-tenant")
def invite_tenant_login(
    payload: InviteTenantIn,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    _sub=Depends(require_subscription_write),
    _role=Depends(require_roles("owner", "manager")),
):
    tenant = db.query(models.Tenant).filter(models.Tenant.org_id == oid, models.Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    email = str(payload.email).lower().strip()

    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = models.User(
        org_id=oid,
        email=email,
        hashed_password=hash_password(payload.password),
        role="tenant",
        is_active=True,
    )
    db.add(user); db.commit(); db.refresh(user)

    # Link tenant to login: email match is primary; user_id optional if your schema has it
    try:
        tenant.email = email
    except Exception:
        pass
    if hasattr(tenant, "user_id"):
        try:
            tenant.user_id = user.id
        except Exception:
            pass

    db.commit()
    return {"ok": True, "tenant_id": tenant.id, "user_id": user.id, "email": email, "temp_password": payload.password}

@router.put("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    _sub=Depends(require_subscription_write),
    _role=Depends(require_roles("owner")),
):
    user = db.query(models.User).filter(models.User.org_id == oid, models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot deactivate owner")
    user.is_active = False
    db.commit(); db.refresh(user)
    return user
