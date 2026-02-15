from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/tenants", tags=["tenants"])

class TenantCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None

class TenantUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None
    is_active: bool | None = None

@router.get("")
def list_(db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_read)):
    return db.query(models.Tenant).filter(models.Tenant.org_id==oid).order_by(models.Tenant.id.desc()).all()

@router.post("")
def create_(payload: TenantCreate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    if not (payload.first_name or "").strip(): raise HTTPException(status_code=422, detail="first_name required")
    if not (payload.last_name or "").strip(): raise HTTPException(status_code=422, detail="last_name required")
    obj = models.Tenant(org_id=oid, **payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{tid}")
def update_(tid: int, payload: TenantUpdate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Tenant).filter(models.Tenant.org_id==oid, models.Tenant.id==tid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    for k,v in payload.dict(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{tid}")
def delete_(tid: int, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Tenant).filter(models.Tenant.org_id==oid, models.Tenant.id==tid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj); db.commit()
    return {"ok": True}
