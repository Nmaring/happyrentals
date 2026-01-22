# backend/app/tenants/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr


class TenantBase(BaseModel):
    # Legacy DB may require this (tenants.unit_id NOT NULL). Keep optional at API level.
    unit_id: Optional[int] = None

    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    unit_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class TenantOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
