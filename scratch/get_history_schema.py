import sqlite3
conn = sqlite3.connect('instance/lpu.db')
print(conn.execute("SELECT sql FROM sqlite_master WHERE name='order_status_history'").fetchone()[0])
conn.close()
