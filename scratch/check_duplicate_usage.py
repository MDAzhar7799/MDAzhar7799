import sqlite3
import os

DATABASE = "instance/lpu.db"
if os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    print("CHECKING SHOP ID 3:")
    items = conn.execute("SELECT COUNT(*) as count FROM food_items WHERE shop_id = 3").fetchone()
    orders = conn.execute("SELECT COUNT(*) as count FROM orders WHERE shop_id = 3").fetchone()
    print(f"ID 3: Items: {items['count']}, Orders: {orders['count']}")
    
    print("\nCHECKING SHOP ID 2:")
    items2 = conn.execute("SELECT COUNT(*) as count FROM food_items WHERE shop_id = 2").fetchone()
    orders2 = conn.execute("SELECT COUNT(*) as count FROM orders WHERE shop_id = 2").fetchone()
    print(f"ID 2: Items: {items2['count']}, Orders: {orders2['count']}")
    
    conn.close()
