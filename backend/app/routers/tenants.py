from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps_auth import get_current_user
from app.models import Tenant, Unit
from app.schemas import TenantCreate, TenantOut, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=List[TenantOut])
def list_tenants(
    unit_id: Optional[int] = Query(default=None),
    property_id: Optional[int] = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Tenant)

    if unit_id is not None:
        q = q.filter(Tenant.unit_id == unit_id)

    if property_id is not None:
        q = q.join(Unit, Tenant.unit_id == Unit.id).filter(Unit.property_id == property_id)

    if not include_inactive:
        q = q.filter(Tenant.is_active == True)  # noqa: E712

    return q.order_by(Tenant.id.asc()).all()


@router.post("", response_model=TenantOut)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    u = db.query(Unit).filter(Unit.id == payload.unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Unit not found")

    t = Tenant(
        unit_id=payload.unit_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        lease_start=payload.lease_start,
        lease_end=payload.lease_end,
        rent=payload.rent,
        deposit=payload.deposit,
        notes=payload.notes,
        is_active=True,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/{tenant_id}", response_model=TenantOut)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    t: Optional[Tenant] = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")

    data = payload.model_dump(exclude_unset=True)

    if "unit_id" in data and data["unit_id"] is not None:
        u = db.query(Unit).filter(Unit.id == data["unit_id"]).first()
        if not u:
            raise HTTPException(status_code=404, detail="Unit not found")

    for k, v in data.items():
        setattr(t, k, v)

    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{tenant_id}/deactivate", response_model=TenantOut)
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    t: Optional[Tenant] = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")

    t.is_active = False
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{tenant_id}/activate", response_model=TenantOut)
def activate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    t: Optional[Tenant] = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")

    t.is_active = True
    db.add(t)
    db.commit()
    db.refresh(t)
    return t
