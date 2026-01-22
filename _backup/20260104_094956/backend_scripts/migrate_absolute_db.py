import sqlite3
from pathlib import Path

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
print("USING DB:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

def table_exists(name):
    return cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

def cols(table):
    return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}

def add_col(table, col, decl):
    if col in cols(table):
        print(f"OK {table}.{col}")
        return
    print(f"ADD {table}.{col} {decl}")
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")

# units
if table_exists("units"):
    add_col("units", "label", "TEXT")
    add_col("units", "bedrooms", "INTEGER")
    add_col("units", "bathrooms", "REAL")
    add_col("units", "sqft", "INTEGER")
    add_col("units", "rent", "REAL")
    add_col("units", "status", "TEXT")
    add_col("units", "notes", "TEXT")

    cur.execute("""
      UPDATE units
      SET label = COALESCE(NULLIF(TRIM(label), ''), 'Unit ' || id)
      WHERE label IS NULL OR TRIM(label) = ''
    """)
    cur.execute("""
      UPDATE units
      SET status = COALESCE(NULLIF(TRIM(status), ''), 'vacant')
      WHERE status IS NULL OR TRIM(status) = ''
    """)

# leases
if table_exists("leases"):
    add_col("leases", "state", "TEXT")
    add_col("leases", "lease_type", "TEXT")
    add_col("leases", "term_months", "INTEGER")
    add_col("leases", "security_deposit", "REAL")
    add_col("leases", "rent_due_day", "INTEGER")
    add_col("leases", "clauses_json", "TEXT")

    cur.execute("UPDATE leases SET state = COALESCE(NULLIF(TRIM(state),''), 'MN')")
    cur.execute("UPDATE leases SET lease_type = COALESCE(NULLIF(TRIM(lease_type),''), 'fixed_term')")
    cur.execute("UPDATE leases SET rent_due_day = COALESCE(rent_due_day, 1) WHERE rent_due_day IS NULL")
    cur.execute("UPDATE leases SET clauses_json = COALESCE(clauses_json, '{}') WHERE clauses_json IS NULL")

# payments (so /payments won’t 500 due to missing cols)
if table_exists("payments"):
    add_col("payments", "lease_id", "INTEGER")
    add_col("payments", "tenant_id", "INTEGER")
    add_col("payments", "unit_id", "INTEGER")
    add_col("payments", "amount", "REAL")
    add_col("payments", "payment_date", "TEXT")
    add_col("payments", "method", "TEXT")
    add_col("payments", "status", "TEXT")
    add_col("payments", "notes", "TEXT")
    add_col("payments", "external_ref", "TEXT")

conn.commit()

for t in ("units","leases","payments"):
    if table_exists(t):
        print(t, "cols:", [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()])

conn.close()
print("DONE")
