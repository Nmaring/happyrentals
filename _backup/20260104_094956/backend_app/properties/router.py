# backend/app/properties/router.py
import importlib
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.properties import models, schemas


def _import_attr(module_candidates: list[str], attr: str):
    last_err = None
    for modname in module_candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, attr):
                return getattr(mod, attr)
        except Exception as e:
            last_err = e
            continue
    raise ImportError(f"Could not import '{attr}' from any of: {module_candidates}. Last error: {last_err}")


get_db = _import_attr(
    [
        "app.db",
        "app.database",
        "app.db.session",
        "app.db.database",
        "app.core.db",
        "app.core.database",
    ],
    "get_db",
)

router = APIRouter(prefix="/properties", tags=["properties"])


def _dump(model_obj, *, exclude_unset: bool = False) -> dict:
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump(exclude_unset=exclude_unset)  # type: ignore
    return model_obj.dict(exclude_unset=exclude_unset)  # type: ignore


def _clean_payload(data: dict) -> dict:
    """
    Trim strings; normalize empty strings to None for optional fields.
    """
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, str):
            v2 = v.strip()
            cleaned[k] = v2
        else:
            cleaned[k] = v
    # normalize optionals
    for k in ("address2", "notes"):
        if k in cleaned and isinstance(cleaned[k], str) and cleaned[k] == "":
            cleaned[k] = None
    return cleaned


@router.get("", response_model=List[schemas.PropertyOut])
def list_properties(db: Session = Depends(get_db)):
    return db.query(models.Property).order_by(models.Property.id.desc()).all()


@router.post("", response_model=schemas.PropertyOut)
def create_property(payload: schemas.PropertyCreate, db: Session = Depends(get_db)):
    data = _clean_payload(_dump(payload))
    obj = models.Property(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{property_id}", response_model=schemas.PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return obj


@router.put("/{property_id}", response_model=schemas.PropertyOut)
def update_property(property_id: int, payload: schemas.PropertyUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Property not found")

    data = _clean_payload(_dump(payload, exclude_unset=True))
    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Property not found")

    db.delete(obj)
    db.commit()
    return {"ok": True}
