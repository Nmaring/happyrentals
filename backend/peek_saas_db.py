import sqlite3
c=sqlite3.connect("saas.db")
print("users:", c.execute("select id,email,role,is_active,created_at from saas_users").fetchall())
try:
    print("orgs:", c.execute("select * from saas_orgs").fetchall())
except Exception as e:
    print("orgs query error:", e)
c.close()
