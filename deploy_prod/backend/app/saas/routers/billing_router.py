from __future__ import annotations
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, get_current_user, require_roles, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/billing", tags=["billing"])

def _sub(db: Session, oid: int) -> models.Subscription:
    sub = db.query(models.Subscription).filter(models.Subscription.org_id == oid).first()
    if not sub:
        sub = models.Subscription(org_id=oid, plan_type="per_unit", status="trialing")
        db.add(sub); db.commit(); db.refresh(sub)
    return sub

@router.get("/usage")
def usage(
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_read),
):
    require_roles(user, ["owner", "manager"])
    sub = _sub(db, oid)
    units = db.query(models.Unit).filter(models.Unit.org_id == oid, models.Unit.is_active == True).count()
    tenants = db.query(models.Tenant).filter(models.Tenant.org_id == oid, models.Tenant.is_active == True).count()
    return {
        "plan_type": sub.plan_type,
        "status": sub.status,
        "billable_units": units,
        "billable_tenants": tenants,
    }

@router.post("/set-plan")
def set_plan(
    plan: dict,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_write),
):
    require_roles(user, ["owner"])
    plan_type = (plan.get("plan_type") or "").strip()
    if plan_type not in ("per_unit", "per_tenant", "flat"):
        raise HTTPException(status_code=422, detail="plan_type must be per_unit|per_tenant|flat")
    sub = _sub(db, oid)
    sub.plan_type = plan_type
    db.commit()
    return {"ok": True, "plan_type": plan_type}

@router.post("/checkout")
def checkout(
    body: dict,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_write),
):
    require_roles(user, ["owner", "manager"])

    # Stripe later – keep endpoint stable
    if not (os.getenv("STRIPE_SECRET_KEY") or "").strip():
        raise HTTPException(status_code=500, detail="Stripe not configured")

    # When you’re ready, this returns {url: "<stripe checkout url>"}
    return {"url": None}
