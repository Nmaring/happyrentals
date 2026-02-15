# backend/app/units/router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, insert, update
from sqlalchemy.exc import SQLAlchemyError

from app.db_compat import get_db
from app.units.models import units, init_units_tables
from app.units.schemas import UnitCreate, UnitUpdate, UnitOut

router = APIRouter(prefix="/units", tags=["units"])

@router.on_event("startup")
def _startup():
    init_units_tables()

def _row_to_out(row) -> UnitOut:
    m = dict(row._mapping)
    if m.get("bathrooms") is not None:
        m["bathrooms"] = float(m["bathrooms"])
    if m.get("rent") is not None:
        m["rent"] = float(m["rent"])
    if not (m.get("label") or "").strip():
        m["label"] = f"Unit {m.get('id')}"
    return UnitOut(**m)

@router.get("", response_model=List[UnitOut])
def list_units(
    property_id: Optional[int] = Query(default=None),
    db=Depends(get_db),
):
    try:
        stmt = select(units)
        if property_id is not None:
            stmt = stmt.where(units.c.property_id == property_id)
        rows = db.execute(stmt.order_by(units.c.id.desc())).fetchall()
        return [_row_to_out(r) for r in rows]
    except Exception as e:
        # show actual failure reason
        raise HTTPException(status_code=500, detail=f"/units failed: {type(e).__name__}: {str(e)}")

@router.post("", response_model=UnitOut)
def create_unit(payload: UnitCreate, db=Depends(get_db)):
    label = (payload.label or "").strip() or "Unit"
    try:
        res = db.execute(
            insert(units).values(
                property_id=payload.property_id,
                label=label,
                bedrooms=payload.bedrooms,
                bathrooms=payload.bathrooms,
                sqft=payload.sqft,
                rent=payload.rent,
                status=payload.status,
                notes=payload.notes,
            )
        )
        db.commit()
        new_id = res.inserted_primary_key[0]
        row = db.execute(select(units).where(units.c.id == new_id)).fetchone()
        return _row_to_out(row)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error creating unit: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"create_unit failed: {type(e).__name__}: {str(e)}")

@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(unit_id: int, payload: UnitUpdate, db=Depends(get_db)):
    try:
        existing = db.execute(select(units).where(units.c.id == unit_id)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Unit not found")

        values = payload.model_dump(exclude_unset=True)
        if "label" in values and values["label"] is not None:
            values["label"] = values["label"].strip() or f"Unit {unit_id}"

        db.execute(update(units).where(units.c.id == unit_id).values(**values))
        db.commit()
        row = db.execute(select(units).where(units.c.id == unit_id)).fetchone()
        return _row_to_out(row)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"update_unit failed: {type(e).__name__}: {str(e)}")






