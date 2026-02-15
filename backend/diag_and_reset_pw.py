import sqlite3, pathlib, inspect, sys
import app.saas.auth as sa

EMAIL = "owner@example.com"
PW    = "YourPass123!"   # must match what you try via curl

print("python:", sys.executable)
print("cwd:", pathlib.Path().resolve())
print("saas.auth module file:", sa.__file__)
print("hash_password file:", inspect.getsourcefile(sa.hash_password))
print("verify_password file:", inspect.getsourcefile(sa.verify_password))

db = pathlib.Path("saas.db").resolve()
print("db:", db, "exists:", db.exists())

con = sqlite3.connect(str(db))
cur = con.cursor()

row = cur.execute("SELECT email, hashed_password, is_active FROM saas_users WHERE email=?", (EMAIL,)).fetchone()
print("user row:", (row[0], (row[1] or "")[:25]+"...", row[2]) if row else None)

if not row:
    raise SystemExit("No user row found for "+EMAIL)

stored_hash = row[1]
print("verify(stored):", sa.verify_password(PW, stored_hash))

# Always rewrite to remove doubt
new_hash = sa.hash_password(PW)
print("new hash prefix:", new_hash[:25]+"...")
print("verify(new):", sa.verify_password(PW, new_hash))

cur.execute("UPDATE saas_users SET hashed_password=? WHERE email=?", (new_hash, EMAIL))
con.commit()

row2 = cur.execute("SELECT email, hashed_password FROM saas_users WHERE email=?", (EMAIL,)).fetchone()
print("after update hash prefix:", row2[1][:25]+"...")

con.close()
print("done")
