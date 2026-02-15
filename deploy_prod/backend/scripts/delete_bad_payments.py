import sqlite3
from pathlib import Path

db_path = Path(r"C:\HappyRentals\backend\happyrentals.db").resolve()
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
cur.execute("DELETE FROM payments WHERE lease_id=0")
conn.commit()
print("✅ deleted payments with lease_id=0:", cur.rowcount)
conn.close()
