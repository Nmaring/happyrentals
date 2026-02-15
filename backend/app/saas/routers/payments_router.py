from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/payments", tags=["payments"])

class PaymentCreate(BaseModel):
    lease_id: int
    amount: float
    payment_date: str
    method: str | None = None
    notes: str | None = None

@router.get("")
def list_(month: str | None = Query(default=None), db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_read)):
    q = db.query(models.Payment).filter(models.Payment.org_id==oid)
    if month:
        q = q.filter(models.Payment.payment_date.like(f"{month}%"))
    return q.order_by(models.Payment.id.desc()).all()

@router.post("")
def create_(payload: PaymentCreate, db: Session = Depends(get_db), oid: int = Depends(org_id), _=Depends(require_subscription_write)):
    obj = models.Payment(org_id=oid, **payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj
