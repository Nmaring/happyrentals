import sqlite3, pathlib
import app.saas.auth as sa

EMAIL="owner@example.com"
PW="YourPass123!"

db = pathlib.Path("saas.db").resolve()
con = sqlite3.connect(str(db))
cur = con.cursor()

row = cur.execute("SELECT email, hashed_password FROM saas_users WHERE email=?", (EMAIL,)).fetchone()
print("before hash prefix:", (row[1] or "")[:25]+"...")

new_hash = sa.hash_password(PW)
print("new hash prefix:", new_hash[:25]+"...")
print("verify(new):", sa.verify_password(PW, new_hash))

cur.execute("UPDATE saas_users SET hashed_password=? WHERE email=?", (new_hash, EMAIL))
con.commit()

row2 = cur.execute("SELECT email, hashed_password FROM saas_users WHERE email=?", (EMAIL,)).fetchone()
print("after hash prefix:", row2[1][:25]+"...")

con.close()
print("done")
