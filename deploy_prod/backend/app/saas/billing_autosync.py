from __future__ import annotations

from sqlalchemy.orm import Session
from app.saas.config import settings
from app.saas import models

def _counts(db: Session, org_id: int) -> tuple[int, int]:
    units = db.query(models.Unit).filter(models.Unit.org_id == org_id, models.Unit.is_active == True).count()
    tenants = db.query(models.Tenant).filter(models.Tenant.org_id == org_id, models.Tenant.is_active == True).count()
    return units, tenants

def maybe_sync_stripe_quantity(db: Session, org_id: int) -> dict:
    """
    Best-effort: keep Stripe subscription quantity in sync with billable usage.
    - No-ops if Stripe not configured
    - No-ops if org not subscribed yet (missing stripe_item_id/subscription_id)
    - Updates quantity based on org subscription plan_type (per_unit / per_tenant)
    """
    if not settings.STRIPE_SECRET_KEY:
        return {"ok": False, "reason": "stripe_not_configured"}

    sub = db.query(models.Subscription).filter(models.Subscription.org_id == org_id).first()
    if not sub:
        return {"ok": False, "reason": "no_subscription_row"}
    if not sub.stripe_subscription_id or not sub.stripe_item_id:
        return {"ok": False, "reason": "not_subscribed_yet"}

    units, tenants = _counts(db, org_id)
    qty = units if (sub.plan_type or "per_unit") == "per_unit" else tenants
    qty = max(1, int(qty))

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.SubscriptionItem.modify(sub.stripe_item_id, quantity=qty)
        return {"ok": True, "plan_type": sub.plan_type, "quantity": qty, "units": units, "tenants": tenants}
    except Exception as e:
        # don't break normal CRUD if Stripe hiccups
        return {"ok": False, "reason": "stripe_error", "error": str(e)}
