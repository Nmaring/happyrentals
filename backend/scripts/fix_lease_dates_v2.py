import re
import sqlite3
from pathlib import Path
from datetime import date

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
print("USING DB:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

def table_exists(name):
    return cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def normalize_date(val, fallback=None, allow_null=True):
    if val is None:
        return None if allow_null else fallback
    s = str(val).strip()
    if not s:
        return None if allow_null else fallback

    # If datetime string, keep just date part
    s = s.split("T")[0].split(" ")[0]

    if ISO.match(s):
        return s

    # YYYY-M-D
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        y, mo, da = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(da):02d}"

    # Digits-only salvage (handles weird values like '2026-12031' -> digits '202612031')
    digits = "".join(ch for ch in s if ch.isdigit())
    if len(digits) == 8:
        y, mo, da = digits[:4], digits[4:6], digits[6:8]
        return f"{int(y):04d}-{int(mo):02d}-{int(da):02d}"
    if len(digits) == 9 and digits.startswith(("19","20")):
        # take YYYY + MM + DD from last 2 digits (ignore the extra middle digit)
        y, mo, da = digits[:4], digits[4:6], digits[-2:]
        return f"{int(y):04d}-{int(mo):02d}-{int(da):02d}"

    return None if allow_null else fallback

if table_exists("leases"):
    rows = cur.execute("SELECT id, start_date, end_date, created_at FROM leases").fetchall()
    fixed = 0
    bad = 0
    today = date.today().isoformat()

    for lease_id, start_date, end_date, created_at in rows:
        ns = normalize_date(start_date, fallback=today, allow_null=False)
        ne = normalize_date(end_date, fallback=None, allow_null=True)
        nc = normalize_date(created_at, fallback=today, allow_null=False)

        if not ISO.match(ns):
            bad += 1
            ns = today
        if ne is not None and not ISO.match(ne):
            bad += 1
            ne = None
        if not ISO.match(nc):
            bad += 1
            nc = today

        if (ns != str(start_date).strip() if start_date is not None else True) or (ne != str(end_date).strip() if end_date is not None else True) or (nc != str(created_at).strip() if created_at is not None else True):
            cur.execute("UPDATE leases SET start_date=?, end_date=?, created_at=? WHERE id=?", (ns, ne, nc, lease_id))
            fixed += 1

    conn.commit()
    print(f"✅ leases rows updated: {fixed} (bad fields corrected: {bad})")
else:
    print("leases table not found (skipping)")

conn.close()
print("DONE")
