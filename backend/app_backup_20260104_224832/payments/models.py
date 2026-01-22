from __future__ import annotations
﻿from datetime import date, datetime

def _date_str(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str):
        s = v.strip()
        return s[:10]  # YYYY-MM-DD
    return str(v)

# backend/app/payments/models.py
from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, Date, Numeric
from sqlalchemy import text

from app.db_compat import metadata, engine

payments = Table(
    "payments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("lease_id", Integer, nullable=False),

    Column("tenant_id", Integer, nullable=True),
    Column("unit_id", Integer, nullable=True),

    Column("amount", Numeric(12, 2), nullable=False),
    Column("payment_date", String(10), nullable=False),  # store as YYYY-MM-DD for sqlite simplicity
    Column("payment_month", String(7), nullable=True),   # YYYY-MM

    Column("method", String(32), nullable=False, default="cash"),
    Column("channel", String(32), nullable=False, default="manual"),
    Column("processor", String(64), nullable=False, default="none"),
    Column("external_reference", String(128), nullable=True),

    Column("payer_handle", String(128), nullable=True),
    Column("account_last4", String(8), nullable=True),

    Column("fee", Numeric(12, 2), nullable=False, default=0),
    Column("currency", String(8), nullable=False, default="USD"),
    Column("status", String(32), nullable=False, default="completed"),
    Column("notes", Text, nullable=True),

    Column("created_at", String(32), nullable=True),
)

def _has_col(conn, table: str, col: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == col for r in rows)

def _add_col(conn, table: str, col: str, ddl: str):
    if not _has_col(conn, table, col):
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))

def init_payments_tables():
    metadata.create_all(engine)
    with engine.begin() as conn:
        # Ensure columns exist for older DBs
        _add_col(conn, "payments", "channel", "channel TEXT")
        _add_col(conn, "payments", "processor", "processor TEXT")
        _add_col(conn, "payments", "external_reference", "external_reference TEXT")
        _add_col(conn, "payments", "created_at", "created_at TEXT")
        _add_col(conn, "payments", "tenant_id", "tenant_id INTEGER")
        _add_col(conn, "payments", "unit_id", "unit_id INTEGER")
        _add_col(conn, "payments", "payer_handle", "payer_handle TEXT")
        _add_col(conn, "payments", "account_last4", "account_last4 TEXT")
        _add_col(conn, "payments", "fee", "fee REAL")
        _add_col(conn, "payments", "currency", "currency TEXT")
        _add_col(conn, "payments", "payment_month", "payment_month TEXT")

        # Backfill defaults
        conn.execute(text("""
            UPDATE payments
            SET channel = COALESCE(NULLIF(TRIM(channel), ''), 'manual')
            WHERE channel IS NULL OR TRIM(channel) = ''
        """))
        conn.execute(text("""
            UPDATE payments
            SET processor = COALESCE(NULLIF(TRIM(processor), ''), 'none')
            WHERE processor IS NULL OR TRIM(processor) = ''
        """))
        conn.execute(text("""
            UPDATE payments
            SET created_at = COALESCE(NULLIF(TRIM(created_at), ''), datetime('now'))
            WHERE created_at IS NULL OR TRIM(created_at) = ''
        """))
        conn.execute(text("""
            UPDATE payments
            SET fee = COALESCE(fee, 0)
            WHERE fee IS NULL
        """))
        conn.execute(text("""
            UPDATE payments
            SET currency = COALESCE(NULLIF(TRIM(currency), ''), 'USD')
            WHERE currency IS NULL OR TRIM(currency) = ''
        """))

