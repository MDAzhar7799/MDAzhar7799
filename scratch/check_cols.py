import sqlite3
DATABASE = "instance/lpu.db"
conn = sqlite3.connect(DATABASE)
cursor = conn.execute("PRAGMA table_info(orders)")
cols = [row[1] for row in cursor.fetchall()]
print(f"Columns in 'orders': {cols}")
conn.close()
