import sqlite3
from pathlib import Path

db = Path("saas.db")
con = sqlite3.connect(str(db))
cur = con.cursor()

def addcol(table, col, typ):
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if col not in cols:
        print(f"adding {table}.{col}")
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    else:
        print(f"exists {table}.{col}")

addcol("saas_subscriptions", "stripe_price_id", "TEXT")

con.commit()
con.close()
print("done")
