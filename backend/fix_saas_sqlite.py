import sqlite3, pathlib

db = pathlib.Path("saas.db")
print("db:", db.resolve(), "exists:", db.exists())

con = sqlite3.connect(str(db))
cur = con.cursor()

cur.execute("PRAGMA table_info(saas_users)")
cols = [r[1] for r in cur.fetchall()]
print("before:", cols)

needed = [("invite_token","TEXT"), ("invite_expires_at","TEXT")]
for col, typ in needed:
    if col not in cols:
        print("adding:", col)
        cur.execute(f"ALTER TABLE saas_users ADD COLUMN {col} {typ}")

con.commit()

cur.execute("PRAGMA table_info(saas_users)")
print("after:", [r[1] for r in cur.fetchall()])

con.close()
print("done")
