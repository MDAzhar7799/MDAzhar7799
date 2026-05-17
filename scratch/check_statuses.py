import sqlite3

DATABASE = "instance/lpu.db"

def check_statuses():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("SELECT DISTINCT order_status FROM orders")
    statuses = cursor.fetchall()
    print("Statuses in DB:")
    for status in statuses:
        print(f"- {status[0]}")
    conn.close()

if __name__ == "__main__":
    check_statuses()
