import sqlite3
import os

DATABASE = "instance/lpu.db"

def test_update_status():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    order_id = 42
    status = 'User Cancelled'
    notes = 'Cancelled by customer'
    updated_by = 'Customer'
    
    try:
        # Update main order status
        conn.execute(
            "UPDATE orders SET order_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, order_id)
        )
        
        # Insert into history
        conn.execute(
            "INSERT INTO order_status_history (order_id, status, notes, updated_by) VALUES (?, ?, ?, ?)",
            (order_id, status, notes, updated_by)
        )
        conn.commit()
        print("Update successful")
    except Exception as e:
        conn.rollback()
        print(f"Error updating order status: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_update_status()
