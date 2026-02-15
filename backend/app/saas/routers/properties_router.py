from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/properties", tags=["properties"])

class PropertyCreate(BaseModel):
    name: str
    address1: str = ""
    address2: str | None = None
    city: str = ""
    state: str = ""
    zip: str = ""
    notes: str | None = None

class PropertyUpdate(BaseModel):
    name: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    notes: str | None = None
    is_active: bool | None = None

@router.get("")
def list_(db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_read)):
    return db.query(models.Property).filter(models.Property.org_id==oid).order_by(models.Property.id.desc()).all()

@router.post("")
def create_(payload: PropertyCreate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    if not (payload.name or "").strip():
        raise HTTPException(status_code=422, detail="name is required")
    obj = models.Property(org_id=oid, **payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{pid}")
def update_(pid: int, payload: PropertyUpdate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Property).filter(models.Property.org_id==oid, models.Property.id==pid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    for k,v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{pid}")
def delete_(pid: int, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Property).filter(models.Property.org_id==oid, models.Property.id==pid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj); db.commit()
    return {"ok": True}
