import sqlite3
con = sqlite3.connect("saas.db")
cur = con.cursor()
cur.execute("select name from sqlite_master where type='table' order by name")
print([r[0] for r in cur.fetchall()])
con.close()
