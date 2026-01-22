# backend/app/properties/schemas.py
from typing import Optional
from pydantic import BaseModel

# Pydantic v2 compatibility
try:
    from pydantic import ConfigDict  # type: ignore
    _HAS_CONFIGDICT = True
except Exception:  # pragma: no cover
    _HAS_CONFIGDICT = False


class PropertyBase(BaseModel):
    name: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str
    notes: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    notes: Optional[str] = None


class PropertyOut(PropertyBase):
    id: int

    # Pydantic v2:
    if _HAS_CONFIGDICT:
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:
        class Config:
            orm_mode = True
