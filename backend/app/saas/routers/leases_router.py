from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/leases", tags=["leases"])

class LeaseCreate(BaseModel):
    unit_id: int
    tenant_id: int | None = None
    monthly_rent: float
    start_date: str | None = None
    end_date: str | None = None
    security_deposit: float | None = None

class LeaseUpdate(BaseModel):
    unit_id: int | None = None
    tenant_id: int | None = None
    monthly_rent: float | None = None
    start_date: str | None = None
    end_date: str | None = None
    security_deposit: float | None = None
    is_active: bool | None = None

@router.get("")
def list_(db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_read)):
    return db.query(models.Lease).filter(models.Lease.org_id==oid).order_by(models.Lease.id.desc()).all()

@router.post("")
def create_(payload: LeaseCreate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    if payload.monthly_rent is None: raise HTTPException(status_code=422, detail="monthly_rent required")
    obj = models.Lease(org_id=oid, **payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{lid}")
def update_(lid: int, payload: LeaseUpdate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Lease).filter(models.Lease.org_id==oid, models.Lease.id==lid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    for k,v in payload.dict(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{lid}")
def delete_(lid: int, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Lease).filter(models.Lease.org_id==oid, models.Lease.id==lid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj); db.commit()
    return {"ok": True}
