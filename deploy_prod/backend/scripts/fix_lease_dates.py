import re
import sqlite3
from pathlib import Path

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
print("USING DB:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

def table_exists(name):
    return cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

def normalize_iso(d: str | None):
    if d is None:
        return None
    d = str(d).strip()
    if not d:
        return None
    # already strict ISO
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        return d
    # fix cases like 2026-1-1 or 2026-01-1 or 2026-1-01
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", d)
    if m:
        y, mo, da = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(da):02d}"
    return d  # leave unknown formats as-is

if table_exists("leases"):
    rows = cur.execute("SELECT id, start_date, end_date, created_at FROM leases").fetchall()
    fixed = 0
    for lease_id, start_date, end_date, created_at in rows:
        ns = normalize_iso(start_date)
        ne = normalize_iso(end_date)
        nc = normalize_iso(created_at)
        if ns != start_date or ne != end_date or nc != created_at:
            cur.execute(
                "UPDATE leases SET start_date=?, end_date=?, created_at=? WHERE id=?",
                (ns, ne, nc, lease_id),
            )
            fixed += 1
    conn.commit()
    print(f"✅ leases normalized rows: {fixed}")
else:
    print("leases table not found (skipping)")

conn.close()
print("DONE")
