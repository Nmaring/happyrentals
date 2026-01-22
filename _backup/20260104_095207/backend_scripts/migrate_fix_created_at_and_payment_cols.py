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

# ---- leases: add created_at ----
if table_exists("leases"):
    add_col("leases", "created_at", "TEXT")
    # backfill to now if null/blank
    cur.execute("""
        UPDATE leases
        SET created_at = COALESCE(NULLIF(TRIM(created_at), ''), datetime('now'))
        WHERE created_at IS NULL OR TRIM(created_at) = ''
    """)

# ---- payments: add the columns your SELECT references ----
if table_exists("payments"):
    add_col("payments", "channel", "TEXT")              # cash / digital / bank / card
    add_col("payments", "processor", "TEXT")            # stripe / plaid / manual / etc
    add_col("payments", "external_reference", "TEXT")   # receipt id / txn id
    add_col("payments", "created_at", "TEXT")

    # backfill defaults
    cur.execute("""
        UPDATE payments
        SET channel = COALESCE(NULLIF(TRIM(channel), ''), 'manual')
        WHERE channel IS NULL OR TRIM(channel) = ''
    """)
    cur.execute("""
        UPDATE payments
        SET processor = COALESCE(NULLIF(TRIM(processor), ''), 'none')
        WHERE processor IS NULL OR TRIM(processor) = ''
    """)
    cur.execute("""
        UPDATE payments
        SET created_at = COALESCE(NULLIF(TRIM(created_at), ''), datetime('now'))
        WHERE created_at IS NULL OR TRIM(created_at) = ''
    """)

conn.commit()

for t in ("leases","payments"):
    if table_exists(t):
        print(t, "cols:", [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()])

conn.close()
print("DONE")
