# backend/app/units/schemas.py
from typing import Optional
from pydantic import BaseModel, Field

class UnitCreate(BaseModel):
    property_id: int
    label: str = Field(default="Unit", min_length=1, max_length=64)

    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    rent: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class UnitUpdate(BaseModel):
    label: Optional[str] = Field(default=None, min_length=1, max_length=64)
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    rent: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class UnitOut(BaseModel):
    id: int
    property_id: int
    label: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    rent: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
