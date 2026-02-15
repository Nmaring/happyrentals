import sqlite3
from datetime import datetime

con = sqlite3.connect("saas.db")
cur = con.cursor()

org_id = 1

# see what columns exist
cur.execute("PRAGMA table_info(saas_subscriptions)")
info = cur.fetchall()
cols = [r[1] for r in info]
print("subscription columns:", cols)

row = cur.execute("SELECT id, org_id, plan_type, status FROM saas_subscriptions WHERE org_id=?", (org_id,)).fetchone()
print("existing:", row)

if not row:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # insert only columns that exist
    insert_cols = []
    insert_vals = []
    def add(col, val):
        if col in cols:
            insert_cols.append(col); insert_vals.append(val)

    add("org_id", org_id)
    add("plan_type", "free")
    add("status", "active")
    add("trial_ends_at", None)
    add("stripe_customer_id", None)
    add("stripe_subscription_id", None)
    add("stripe_price_id", None)
    add("created_at", now)

    q = f"INSERT INTO saas_subscriptions ({', '.join(insert_cols)}) VALUES ({', '.join(['?']*len(insert_cols))})"
    cur.execute(q, insert_vals)
    con.commit()
    print("inserted subscription for org_id=1")

row2 = cur.execute("SELECT * FROM saas_subscriptions WHERE org_id=?", (org_id,)).fetchall()
print("after:", row2)

con.close()
