from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps_auth import get_current_user
from app.models import Unit, Property
from app.schemas import UnitCreate, UnitOut, UnitUpdate

router = APIRouter(prefix="/units", tags=["units"])


@router.get("", response_model=List[UnitOut])
def list_units(
    property_id: int,
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Unit).filter(Unit.property_id == property_id)
    if not include_inactive:
        q = q.filter(Unit.is_active == True)  # noqa: E712
    return q.order_by(Unit.id.asc()).all()


@router.post("", response_model=UnitOut)
def create_unit(
    payload: UnitCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    u = Unit(
        property_id=payload.property_id,
        unit_number=payload.unit_number,
        bedrooms=payload.bedrooms,
        bathrooms=payload.bathrooms,
        sqft=payload.sqft,
        rent=payload.rent,
        notes=payload.notes,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(
    unit_id: int,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    u: Optional[Unit] = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Unit not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(u, k, v)

    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.post("/{unit_id}/deactivate", response_model=UnitOut)
def deactivate_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    u: Optional[Unit] = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Unit not found")

    u.is_active = False
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.post("/{unit_id}/activate", response_model=UnitOut)
def activate_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    u: Optional[Unit] = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Unit not found")

    u.is_active = True
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
