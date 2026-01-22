# backend/app/leases/schemas.py
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


LeaseType = Literal["month_to_month", "fixed_term", "open_ended"]
LeaseStatus = Literal["draft", "active", "ended", "terminated"]


class LeaseCreate(BaseModel):
    tenant_id: int
    unit_id: int

    state: str = "MN"
    lease_type: LeaseType = "month_to_month"
    term_months: Optional[int] = None

    # Defaults so UI/POSTs don't error if omitted
    start_date: str = Field(default_factory=lambda: date.today().isoformat())
    end_date: Optional[str] = None

    monthly_rent: float = 0.0
    security_deposit: Optional[float] = 0.0
    rent_due_day: int = 1

    status: LeaseStatus = "active"
    clauses_json: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class LeaseUpdate(BaseModel):
    state: Optional[str] = None
    lease_type: Optional[LeaseType] = None
    term_months: Optional[int] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    monthly_rent: Optional[float] = None
    security_deposit: Optional[float] = None
    rent_due_day: Optional[int] = None

    status: Optional[LeaseStatus] = None
    clauses_json: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class LeaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    unit_id: int

    state: str
    lease_type: str
    term_months: Optional[int] = None

    # IMPORTANT: match DB types coming from SQLAlchemy
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    monthly_rent: float
    security_deposit: Optional[float] = None
    rent_due_day: int = 1

    status: str
    clauses_json: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
