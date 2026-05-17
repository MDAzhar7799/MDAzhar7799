import sqlite3
import os

DATABASE = "instance/lpu.db"
if os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    shops = conn.execute("SELECT id, name, is_active FROM shops").fetchall()
    print("SHOPS IN DATABASE:")
    for shop in shops:
        print(f"ID: {shop['id']}, Name: {shop['name']}, Active: {shop['is_active']}")
    conn.close()
else:
    print(f"Database {DATABASE} not found")
