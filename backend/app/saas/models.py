from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.saas.db import Base

class Organization(Base):
    __tablename__ = "saas_organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class User(Base):
    __tablename__ = "saas_users"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("saas_organizations.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="owner")  # owner|manager|tenant
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    invite_token = Column(String(140), nullable=True, index=True)
    invite_expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_saas_users_org_email", "org_id", "email", unique=True),
    )

class Subscription(Base):
    __tablename__ = "saas_subscriptions"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("saas_organizations.id"), nullable=False, index=True)
    plan_type = Column(String(40), nullable=False, default="per_unit")     # per_unit|per_tenant|flat
    status = Column(String(40), nullable=False, default="trialing")        # trialing|active|past_due|canceled
    trial_ends_at = Column(DateTime, nullable=True)

    stripe_customer_id = Column(String(80), nullable=True)
    stripe_subscription_id = Column(String(80), nullable=True)
    stripe_price_id = Column(String(80), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# SaaS business tables (scoped by org_id)
class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address1 = Column(String(255), nullable=False, default="")
    address2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False, default="")
    state = Column(String(20), nullable=False, default="")
    zip = Column(String(20), nullable=False, default="")
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    property_id = Column(Integer, nullable=False, index=True)
    unit_number = Column(String(50), nullable=False)
    bedrooms = Column(Float, nullable=True)
    bathrooms = Column(Float, nullable=True)
    sq_ft = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Lease(Base):
    __tablename__ = "leases"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    unit_id = Column(Integer, nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    monthly_rent = Column(Float, nullable=False)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    security_deposit = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    lease_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(String(20), nullable=False)
    method = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False, index=True)
    unit_id = Column(Integer, nullable=True, index=True)          # NO FK (keeps create_all stable)
    tenant_user_id = Column(Integer, nullable=True, index=True)   # tenant user id
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), nullable=False, default="normal")
    status = Column(String(30), nullable=False, default="open")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
