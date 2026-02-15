# backend/app/units/models.py
from sqlalchemy import Table, Column, Integer, String, Numeric, Text
from sqlalchemy import text
from app.db_compat import metadata, engine

units = Table(
    "units",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("property_id", Integer, nullable=False),

    Column("label", String(64), nullable=True),   # <-- IMPORTANT
    Column("bedrooms", Integer, nullable=True),
    Column("bathrooms", Numeric(10, 2), nullable=True),
    Column("sqft", Integer, nullable=True),
    Column("rent", Numeric(12, 2), nullable=True),
    Column("status", String(32), nullable=True),
    Column("notes", Text, nullable=True),
)

def _sqlite_has_column(conn, table: str, col: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    # pragma row: (cid, name, type, notnull, dflt_value, pk)
    return any((r[1] == col) for r in rows)

def init_units_tables():
    """
    Ensures:
    - units table exists
    - label column exists
    - existing rows have a default label if missing
    """
    metadata.create_all(bind=engine)

    # If table existed before without 'label', add it (SQLite)
    if engine.url.get_backend_name() == "sqlite":
        with engine.begin() as conn:
            if not _sqlite_has_column(conn, "units", "label"):
                conn.execute(text("ALTER TABLE units ADD COLUMN label VARCHAR(64)"))
            # backfill labels for existing units
            conn.execute(text("""
                UPDATE units
                SET label = COALESCE(NULLIF(TRIM(label), ''), 'Unit ' || id)
                WHERE label IS NULL OR TRIM(label) = ''
            """))
