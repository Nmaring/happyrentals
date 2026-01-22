from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps_auth import get_current_user
from app.models import Property
from app.schemas import PropertyCreate, PropertyOut, PropertyUpdate

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("", response_model=List[PropertyOut])
def list_properties(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Property)
    if not include_inactive:
        q = q.filter(Property.is_active == True)  # noqa: E712
    return q.order_by(Property.id.asc()).all()


@router.post("", response_model=PropertyOut)
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    p = Property(
        name=payload.name,
        address1=payload.address1,
        address2=payload.address2,
        city=payload.city,
        state=payload.state,
        zip=payload.zip,
        notes=payload.notes,
        is_active=True,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    p: Optional[Property] = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)

    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/{property_id}/deactivate", response_model=PropertyOut)
def deactivate_property(
    property_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    p: Optional[Property] = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")

    p.is_active = False
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/{property_id}/activate", response_model=PropertyOut)
def activate_property(
    property_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    p: Optional[Property] = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")

    p.is_active = True
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
