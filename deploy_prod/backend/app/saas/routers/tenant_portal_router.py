from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.deps import get_current_user, require_roles, require_subscription_read

router = APIRouter(prefix="/api/tenant", tags=["tenant"])

@router.get("/me")
def tenant_me(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _sub=Depends(require_subscription_read),
    _role=Depends(require_roles("tenant")),
):
    # Prefer user_id link if it exists, else fallback to email match
    tenant = None
    if hasattr(models.Tenant, "user_id"):
        tenant = db.query(models.Tenant).filter(
            models.Tenant.org_id == user.org_id,
            models.Tenant.user_id == user.id
        ).first()

    if not tenant:
        tenant = db.query(models.Tenant).filter(
            models.Tenant.org_id == user.org_id,
            models.Tenant.email == user.email
        ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant profile not linked to this login (email mismatch)")

    leases = db.query(models.Lease).filter(
        models.Lease.org_id == user.org_id,
        models.Lease.tenant_id == tenant.id
    ).order_by(models.Lease.id.desc()).all()

    return {
        "tenant": {
            "id": tenant.id,
            "first_name": getattr(tenant, "first_name", ""),
            "last_name": getattr(tenant, "last_name", ""),
            "email": tenant.email,
            "phone": getattr(tenant, "phone", None),
            "is_active": getattr(tenant, "is_active", True),
        },
        "leases": [
            {
                "id": l.id,
                "unit_id": l.unit_id,
                "monthly_rent": getattr(l, "monthly_rent", None),
                "start_date": getattr(l, "start_date", None),
                "end_date": getattr(l, "end_date", None),
                "is_active": getattr(l, "is_active", True),
            } for l in leases
        ],
    }
