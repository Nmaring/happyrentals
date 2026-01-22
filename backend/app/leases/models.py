# backend/app/leases/models.py
from sqlalchemy import Table, Column, Integer, String, Date, Numeric, Text, DateTime
from sqlalchemy.sql import func
from app.db_compat import metadata, engine

leases = Table(
    "leases",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("unit_id", Integer, nullable=False),

    Column("state", String(2), nullable=False, server_default="MN"),

    # fixed_term | month_to_month | open_ended
    Column("lease_type", String(32), nullable=False, server_default="fixed_term"),
    Column("term_months", Integer, nullable=True),

    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=True),

    Column("monthly_rent", Numeric(12, 2), nullable=False, server_default="0"),
    Column("security_deposit", Numeric(12, 2), nullable=True),

    Column("rent_due_day", Integer, nullable=False, server_default="1"),
    Column("status", String(32), nullable=False, server_default="draft"),

    # JSON string of clause toggles + values
    Column("clauses_json", Text, nullable=True),

    Column("created_at", DateTime(timezone=False), server_default=func.now(), nullable=False),
    Column("notes", Text, nullable=True),
)

def init_leases_tables():
    metadata.create_all(bind=engine)

# NOTE: could not auto-insert migration block; please add notes migration manually.

