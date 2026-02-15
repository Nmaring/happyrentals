from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/units", tags=["units"])

class UnitCreate(BaseModel):
    property_id: int
    unit_number: str
    bedrooms: float | None = None
    bathrooms: float | None = None
    sq_ft: float | None = None
    notes: str | None = None

class UnitUpdate(BaseModel):
    property_id: int | None = None
    unit_number: str | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
    sq_ft: float | None = None
    notes: str | None = None
    is_active: bool | None = None

@router.get("")
def list_(db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_read)):
    return db.query(models.Unit).filter(models.Unit.org_id==oid).order_by(models.Unit.id.desc()).all()

@router.post("")
def create_(payload: UnitCreate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    if not (payload.unit_number or "").strip(): raise HTTPException(status_code=422, detail="unit_number required")
    obj = models.Unit(org_id=oid, **payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{uid}")
def update_(uid: int, payload: UnitUpdate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Unit).filter(models.Unit.org_id==oid, models.Unit.id==uid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    for k,v in payload.dict(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{uid}")
def delete_(uid: int, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = db.query(models.Unit).filter(models.Unit.org_id==oid, models.Unit.id==uid).first()
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj); db.commit()
    return {"ok": True}
