import sqlite3
import os

# Database path
db_path = 'instance/lpu.db'

# Image path relative to static
image_path = 'uploads/lpu_mess_logo.png'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update the shop logo for LPU Mess
    cursor.execute("UPDATE shops SET logo_path = ? WHERE name LIKE '%LPU Mess%'", ('uploads/lpu_mess_logo.png',))
    
    # Update the shop logo for LawgetShop
    cursor.execute("UPDATE shops SET logo_path = ? WHERE name LIKE '%Lawget%'", ('uploads/lawgate_shop_logo.png',))
    
    if cursor.rowcount >= 0:
        print(f"Database update process completed.")
        
    conn.commit()
    conn.close()
except Exception as e:
    print(f"Error updating database: {e}")
