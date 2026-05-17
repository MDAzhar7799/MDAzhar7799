import sqlite3

DATABASE = "instance/lpu.db"

def check_and_add_column():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "is_notified" not in columns:
        print("Adding column 'is_notified' to orders table...")
        cursor.execute("ALTER TABLE orders ADD COLUMN is_notified INTEGER DEFAULT 0")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column 'is_notified' already exists.")
    
    conn.close()

if __name__ == "__main__":
    check_and_add_column()
