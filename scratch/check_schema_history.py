import sqlite3

DATABASE = "instance/lpu.db"

def check_schema():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("PRAGMA table_info(order_status_history)")
    cols = cursor.fetchall()
    for col in cols:
        print(f"Column: {col[1]}")
    conn.close()

if __name__ == "__main__":
    check_schema()
