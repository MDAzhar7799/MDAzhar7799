import sqlite3
import os

DATABASE = "instance/lpu.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def test_query():
    conn = get_db_connection()
    try:
        # Testing the query I wrote
        orders = conn.execute(
            """SELECT o.*, s.name as shop_name, u.name as customer_name, u.email as customer_email, u.phone as customer_phone
               FROM orders o 
               JOIN shops s ON o.shop_id = s.id 
               JOIN users u ON o.user_id = u.id 
               ORDER BY o.created_at DESC"""
        ).fetchall()
        print(f"Success! Found {len(orders)} orders.")
        for o in orders[:1]:
            print(f"Order Number: {o['order_number']}")
            print(f"Customer: {o['customer_name']}")
            print(f"Email: {o['customer_email']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_query()
