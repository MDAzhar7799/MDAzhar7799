import sqlite3

DATABASE = "instance/lpu.db"

def check_order(order_number):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    order = conn.execute("SELECT * FROM orders WHERE order_number = ?", (order_number,)).fetchone()
    if order:
        print(f"Order: {order['order_number']}")
        print(f"Status: {order['order_status']}")
        
        history = conn.execute("SELECT * FROM order_status_history WHERE order_id = ? ORDER BY created_at DESC", (order['id'],)).fetchall()
        print("\nHistory:")
        for h in history:
            print(f"- Status: {h['status']}, Updated By: {h['updated_by']}, Notes: {h['notes']}")
    else:
        print("Order not found")
    conn.close()

if __name__ == "__main__":
    check_order("FEX2605031437ZPHJ")
