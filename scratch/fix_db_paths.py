import sqlite3
import os

DATABASE = "instance/lpu.db"

def fix_paths():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Fix shops QR paths
    shops = conn.execute("SELECT id, qr_code_path FROM shops").fetchall()
    for shop in shops:
        if shop['qr_code_path']:
            new_path = shop['qr_code_path'].replace('\\', '/')
            if new_path != shop['qr_code_path']:
                conn.execute("UPDATE shops SET qr_code_path = ? WHERE id = ?", (new_path, shop['id']))
                print(f"Fixed Shop {shop['id']} path: {new_path}")
                
    # Fix food items paths
    items = conn.execute("SELECT id, image_path FROM food_items").fetchall()
    for item in items:
        if item['image_path']:
            new_path = item['image_path'].replace('\\', '/')
            if new_path != item['image_path']:
                conn.execute("UPDATE food_items SET image_path = ? WHERE id = ?", (new_path, item['id']))
                print(f"Fixed Item {item['id']} path: {new_path}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_paths()
