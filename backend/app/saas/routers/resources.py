from __future__ import annotations
from app.saas.routers.crud import make_crud
from app.saas import models

properties_router = make_crud(
    "properties",
    models.Property,
    lambda p: {
        "name": p.get("name",""),
        "address1": p.get("address1",""),
        "address2": p.get("address2"),
        "city": p.get("city",""),
        "state": p.get("state",""),
        "zip": p.get("zip",""),
        "notes": p.get("notes"),
        "is_active": p.get("is_active", True),
    },
)

units_router = make_crud(
    "units",
    models.Unit,
    lambda p: {
        "property_id": p.get("property_id"),
        "unit_number": p.get("unit_number",""),
        "bedrooms": p.get("bedrooms"),
        "bathrooms": p.get("bathrooms"),
        "sq_ft": p.get("sq_ft"),
        "notes": p.get("notes"),
        "is_active": p.get("is_active", True),
    },
)

tenants_router = make_crud(
    "tenants",
    models.Tenant,
    lambda p: {
        "first_name": p.get("first_name",""),
        "last_name": p.get("last_name",""),
        "email": p.get("email"),
        "phone": p.get("phone"),
        "notes": p.get("notes"),
        "is_active": p.get("is_active", True),
    },
)

leases_router = make_crud(
    "leases",
    models.Lease,
    lambda p: {
        "unit_id": p.get("unit_id"),
        "tenant_id": p.get("tenant_id"),
        "monthly_rent": p.get("monthly_rent"),
        "start_date": p.get("start_date"),
        "end_date": p.get("end_date"),
        "security_deposit": p.get("security_deposit"),
        "is_active": p.get("is_active", True),
    },
)

payments_router = make_crud(
    "payments",
    models.Payment,
    lambda p: {
        "lease_id": p.get("lease_id"),
        "amount": p.get("amount"),
        "payment_date": p.get("payment_date"),
        "method": p.get("method"),
        "notes": p.get("notes"),
        "status": p.get("status","completed"),
    },
)
