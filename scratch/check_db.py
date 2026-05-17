import sqlite3
import os

DATABASE = "instance/lpu.db"

def check_orders():
    if not os.path.exists(DATABASE):
        print(f"Database not found at {DATABASE}")
        return
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("--- Orders ---")
        orders = cursor.execute("SELECT id, order_number, user_id, order_status FROM orders ORDER BY id DESC LIMIT 5").fetchall()
        for o in orders:
            print(f"ID: {o['id']}, Num: {o['order_number']}, User: {o['user_id']}, Status: {o['order_status']}")
            
        print("\n--- Status History for ID 32 and 33 ---")
        history = cursor.execute("SELECT * FROM order_status_history WHERE order_id IN (32, 33) ORDER BY order_id, created_at DESC").fetchall()
        for h in history:
            print(f"OrderID: {h['order_id']}, Status: {h['status']}, UpdatedBy: {h['updated_by']}, Time: {h['created_at']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_orders()
