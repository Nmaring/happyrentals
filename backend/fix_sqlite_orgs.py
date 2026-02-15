import sqlite3
con = sqlite3.connect("saas.db")
cur = con.cursor()

# org table
cur.execute("""
CREATE TABLE IF NOT EXISTS saas_orgs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at TEXT
)
""")

# add org if none
org = cur.execute("SELECT id FROM saas_orgs LIMIT 1").fetchone()
if not org:
    cur.execute("INSERT INTO saas_orgs (name, created_at) VALUES (?, datetime('now'))", ("HappyRentals",))
    org_id = cur.lastrowid
else:
    org_id = org[0]

# link users to org
cur.execute("UPDATE saas_users SET org_id=? WHERE org_id IS NULL OR org_id=0", (org_id,))

con.commit()
print("org_id=", org_id)
print("orgs:", cur.execute("SELECT * FROM saas_orgs").fetchall())
print("users:", cur.execute("SELECT id,email,org_id,role,is_active FROM saas_users").fetchall())
con.close()
