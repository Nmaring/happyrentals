from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from app.db import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)

    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    lease_start = Column(String, nullable=True)  # "YYYY-MM-DD"
    lease_end = Column(String, nullable=True)    # "YYYY-MM-DD"

    rent = Column(Integer, nullable=True)
    deposit = Column(Integer, nullable=True)

    notes = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
