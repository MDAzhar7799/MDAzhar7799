"""
Database Migration Script - Add new fields to existing tables
Run this script to update your existing database with new columns
"""

import sqlite3
import os

DATABASE = "instance/lpu.db"

def migrate():
    """Add new columns to existing tables"""
    
    # Check if database exists
    if not os.path.exists(DATABASE):
        print(f"Database not found at {DATABASE}")
        print("Please run schema_init.py first to create the database")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        # Check if logo_path column already exists in shops table
        cursor.execute("PRAGMA table_info(shops)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'logo_path' not in columns:
            print("Adding logo_path column to shops table...")
            cursor.execute("ALTER TABLE shops ADD COLUMN logo_path TEXT")
            print("✓ Added logo_path to shops table")
        else:
            print("✓ logo_path already exists in shops table")
        
        # Check if delivery tracking columns exist in orders table
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = ['delivery_boy_name', 'delivery_boy_phone', 'current_location']
        
        for col_name in new_columns:
            if col_name not in columns:
                print(f"Adding {col_name} column to orders table...")
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} TEXT")
                print(f"✓ Added {col_name} to orders table")
            else:
                print(f"✓ {col_name} already exists in orders table")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\nNew features available:")
        print("- Shopkeepers can now upload shop logos")
        print("- Enhanced delivery tracking with delivery boy information")
        print("- Real-time order status updates for customers")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
