import sqlite3
from pathlib import Path

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
print("USING DB:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# created_at default for old rows
cur.execute("""
UPDATE leases
SET created_at = COALESCE(NULLIF(TRIM(created_at), ''), datetime('now'))
WHERE created_at IS NULL OR TRIM(created_at) = ''
""")
print("✅ leases created_at filled:", cur.rowcount)

# security_deposit default (optional — set to 0 when missing)
cur.execute("""
UPDATE leases
SET security_deposit = COALESCE(security_deposit, 0)
WHERE security_deposit IS NULL
""")
print("✅ leases security_deposit filled:", cur.rowcount)

conn.commit()
conn.close()
print("DONE")
