import sqlite3

DATABASE = "instance/lpu.db"

def get_stats():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    stats = {}
    
    stats['total_orders'] = conn.execute("SELECT COUNT(*) FROM orders WHERE order_status != 'User Cancelled'").fetchone()[0]
    stats['active_shops'] = conn.execute("SELECT COUNT(*) FROM shops WHERE is_active = 1").fetchone()[0]
    stats['total_users'] = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]
    stats['total_shopkeepers'] = conn.execute("SELECT COUNT(*) FROM shopkeepers WHERE is_active = 1").fetchone()[0]
    
    conn.close()
    return stats

if __name__ == "__main__":
    print(get_stats())
