import sqlite3
from pathlib import Path

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
print("USING DB:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 1) Backfill tenant_id/unit_id for payments that have a lease_id but missing tenant/unit
cur.execute("""
UPDATE payments
SET
  tenant_id = (SELECT tenant_id FROM leases WHERE leases.id = payments.lease_id),
  unit_id   = (SELECT unit_id   FROM leases WHERE leases.id = payments.lease_id)
WHERE
  lease_id IS NOT NULL
  AND lease_id != 0
  AND (tenant_id IS NULL OR unit_id IS NULL)
""")
print("✅ backfilled tenant/unit rows:", cur.rowcount)

# 2) Normalize channel based on method when channel is NULL or 'manual'
cur.execute("""
UPDATE payments
SET channel = CASE
  WHEN lower(method) = 'cash' THEN 'cash'
  WHEN lower(method) IN ('check','money_order') THEN 'check'
  WHEN lower(method) IN ('ach','wire') THEN 'bank'
  WHEN lower(method) IN ('credit_card','debit_card','card','apple_pay','google_pay') THEN 'card'
  WHEN lower(method) IN ('zelle','venmo','cashapp','paypal') THEN 'p2p'
  ELSE 'manual'
END
WHERE channel IS NULL OR trim(channel) = '' OR lower(channel) = 'manual'
""")
print("✅ normalized channel rows:", cur.rowcount)

conn.commit()

# show a quick sample
rows = cur.execute("""
SELECT id, lease_id, tenant_id, unit_id, method, channel, amount, payment_date
FROM payments
ORDER BY id DESC
LIMIT 10
""").fetchall()

print("\nRecent payments:")
for r in rows:
    print(r)

conn.close()
print("DONE")
