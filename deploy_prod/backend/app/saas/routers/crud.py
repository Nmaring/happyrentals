from __future__ import annotations

from typing import Callable, Type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas.deps import org_id, require_subscription_read, require_subscription_write
from app.saas.billing_autosync import maybe_sync_stripe_quantity


def make_crud(
    name: str,
    model: Type,
    create_fields: Callable[[dict], dict],
) -> APIRouter:
    router = APIRouter(prefix=f"/api/{name}", tags=[name])

    def _maybe_sync(db: Session, oid: int) -> None:
        if name in ("units", "tenants"):
            try:
                maybe_sync_stripe_quantity(db, oid)
            except Exception:
                pass

    @router.get("")
    def list_items(
        db: Session = Depends(get_db),
        oid: int = Depends(org_id),
        _=Depends(require_subscription_read),
    ):
        return db.query(model).filter(model.org_id == oid).order_by(model.id.desc()).all()

    @router.get("/{item_id}")
    def get_item(
        item_id: int,
        db: Session = Depends(get_db),
        oid: int = Depends(org_id),
        _=Depends(require_subscription_read),
    ):
        obj = db.query(model).filter(model.org_id == oid, model.id == item_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{name} not found")
        return obj

    @router.post("")
    def create_item(
        payload: dict,
        db: Session = Depends(get_db),
        oid: int = Depends(org_id),
        _=Depends(require_subscription_write),
    ):
        data = create_fields(payload)
        data["org_id"] = oid
        obj = model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        _maybe_sync(db, oid)
        return obj

    @router.put("/{item_id}")
    def update_item(
        item_id: int,
        payload: dict,
        db: Session = Depends(get_db),
        oid: int = Depends(org_id),
        _=Depends(require_subscription_write),
    ):
        obj = db.query(model).filter(model.org_id == oid, model.id == item_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{name} not found")

        for k, v in payload.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        db.commit()
        db.refresh(obj)
        _maybe_sync(db, oid)
        return obj

    @router.delete("/{item_id}")
    def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        oid: int = Depends(org_id),
        _=Depends(require_subscription_write),
    ):
        obj = db.query(model).filter(model.org_id == oid, model.id == item_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{name} not found")
        db.delete(obj)
        db.commit()
        _maybe_sync(db, oid)
        return {"ok": True}

    return router
