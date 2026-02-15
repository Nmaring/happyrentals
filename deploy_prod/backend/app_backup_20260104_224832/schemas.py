from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---------- AUTH ----------
class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- PROPERTIES ----------
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
    is_active: Optional[bool] = None


class PropertyOut(PropertyBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- UNITS ----------
class UnitCreate(BaseModel):
    property_id: int
    unit_number: str
    bedrooms: int = 0
    bathrooms: float = 0
    sqft: int = 0
    rent: Optional[float] = None
    notes: Optional[str] = None


class UnitUpdate(BaseModel):
    property_id: Optional[int] = None
    unit_number: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    rent: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class UnitOut(BaseModel):
    id: int
    property_id: int
    unit_number: str
    bedrooms: int
    bathrooms: float
    sqft: int
    rent: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- TENANTS ----------
class TenantCreate(BaseModel):
    unit_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_start: Optional[str] = None
    lease_end: Optional[str] = None
    rent: Optional[float] = None
    deposit: Optional[float] = None
    notes: Optional[str] = None


class TenantUpdate(BaseModel):
    unit_id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_start: Optional[str] = None
    lease_end: Optional[str] = None
    rent: Optional[float] = None
    deposit: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TenantOut(BaseModel):
    id: int
    unit_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_start: Optional[str] = None
    lease_end: Optional[str] = None
    rent: Optional[float] = None
    deposit: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# -----------------------------
# HANDOFF NEXT TODO PATCH: Unit label fallback
# -----------------------------
def _unit_label_fallback(u):
    # u may be dict-like or model; handle both
    get = (lambda k: u.get(k)) if hasattr(u, "get") else (lambda k: getattr(u, k, None))
    label = (get("label") or "").strip()
    if label:
        return label
    for k in ["name","unit_number","number"]:
        v = get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    vid = get("id")
    return f"Unit {vid}" if vid is not None else "Unit"

