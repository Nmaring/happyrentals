from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.deps import org_id, get_current_user, require_subscription_read, require_subscription_write

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])

class MRCreate(BaseModel):
    unit_id: int | None = None
    title: str
    description: str | None = None
    priority: str | None = "normal"

class MRUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    title: str | None = None
    description: str | None = None

@router.get("")
def list_requests(
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_read),
):
    q = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.org_id == oid)
    if (user.role or "") == "tenant":
        q = q.filter(models.MaintenanceRequest.tenant_user_id == user.id)
    return q.order_by(models.MaintenanceRequest.id.desc()).all()

@router.post("")
def create_request(
    payload: MRCreate,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_write),
):
    title = (payload.title or "").strip()
    if not title:
        raise HTTPException(status_code=422, detail="title is required")
    pr = (payload.priority or "normal").strip().lower()
    if pr not in ("low","normal","high","urgent"): pr = "normal"

    mr = models.MaintenanceRequest(
        org_id=oid,
        unit_id=payload.unit_id,
        tenant_user_id=(user.id if (user.role or "") == "tenant" else None),
        title=title,
        description=(payload.description or None),
        priority=pr,
        status="open",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(mr); db.commit(); db.refresh(mr)
    return mr

@router.put("/{mr_id}")
def update_request(
    mr_id: int,
    payload: MRUpdate,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_write),
):
    mr = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.org_id==oid, models.MaintenanceRequest.id==mr_id).first()
    if not mr:
        raise HTTPException(status_code=404, detail="Not found")

    if (user.role or "") == "tenant" and mr.tenant_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if (user.role or "") == "tenant":
        if payload.title is not None: mr.title = payload.title.strip()
        if payload.description is not None: mr.description = payload.description
    else:
        if payload.title is not None: mr.title = payload.title.strip()
        if payload.description is not None: mr.description = payload.description
        if payload.priority is not None:
            pr = payload.priority.strip().lower()
            if pr in ("low","normal","high","urgent"): mr.priority = pr
        if payload.status is not None:
            st = payload.status.strip().lower()
            if st in ("open","in_progress","resolved","closed"): mr.status = st

    mr.updated_at = datetime.utcnow()
    db.commit(); db.refresh(mr)
    return mr

@router.delete("/{mr_id}")
def delete_request(
    mr_id: int,
    db: Session = Depends(get_db),
    oid: int = Depends(org_id),
    user=Depends(get_current_user),
    _=Depends(require_subscription_write),
):
    mr = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.org_id==oid, models.MaintenanceRequest.id==mr_id).first()
    if not mr:
        raise HTTPException(status_code=404, detail="Not found")
    if (user.role or "") == "tenant" and mr.tenant_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(mr); db.commit()
    return {"ok": True}
