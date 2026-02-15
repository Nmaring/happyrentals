import sqlite3
from pathlib import Path

db = Path("saas.db")
con = sqlite3.connect(str(db))
cur = con.cursor()

cur.execute("PRAGMA table_info(saas_subscriptions)")
cols = [r[1] for r in cur.fetchall()]
print("cols before:", cols)

if "stripe_price_id" not in cols:
    print("adding stripe_price_id")
    cur.execute("ALTER TABLE saas_subscriptions ADD COLUMN stripe_price_id TEXT")

con.commit()

cur.execute("PRAGMA table_info(saas_subscriptions)")
print("cols after:", [r[1] for r in cur.fetchall()])

con.close()
print("done")
