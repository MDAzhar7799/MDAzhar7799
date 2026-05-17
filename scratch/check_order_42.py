import sqlite3
import os

DATABASE = "instance/lpu.db"

def check_order():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    order = conn.execute("SELECT * FROM orders WHERE id = 42").fetchone()
    if order:
        print(f"Order 42 Status: {order['order_status']}")
        print(f"User ID: {order['user_id']}")
    else:
        print("Order 42 not found")
    
    history = conn.execute("SELECT * FROM order_status_history WHERE order_id = 42").fetchall()
    print("\nStatus History:")
    for h in history:
        print(f"{h['created_at']} - {h['status']} ({h['updated_by']}): {h['notes']}")
    
    conn.close()

if __name__ == "__main__":
    check_order()
