import sqlite3
import os

DATABASE = "instance/lpu.db"
if os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    print("DEACTIVATING DUPLICATE SHOP (ID 2):")
    conn.execute("UPDATE shops SET is_active = 0 WHERE id = 2")
    conn.commit()
    print("Shop ID 2 deactivated.")
    
    result = conn.execute("SELECT COUNT(*) as count FROM shops WHERE is_active = 1").fetchone()
    print(f"NEW ACTIVE SHOP COUNT: {result[0]}")
    
    conn.close()
