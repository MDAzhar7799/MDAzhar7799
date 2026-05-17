import os
from models import get_db_connection

# Ensure instance directory exists
os.makedirs("instance", exist_ok=True)

conn = get_db_connection()
cursor = conn.cursor()

# ============================================
# USERS TABLE - Customer accounts
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
)
""")

# ============================================
# ADMIN TABLE - Super admin credentials
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ============================================
# SHOPKEEPERS TABLE - Shop owner login credentials
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS shopkeepers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
)
""")

# ============================================
# SHOPS TABLE - Shop profiles with QR codes
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopkeeper_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    phone TEXT,
    email TEXT,
    logo_path TEXT,
    qr_code_path TEXT,
    upi_id TEXT,
    delivery_available INTEGER DEFAULT 1,
    delivery_charge REAL DEFAULT 20,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id) ON DELETE CASCADE
)
""")

# ============================================
# FOOD_ITEMS TABLE - Menu items per shop
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS food_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT,
    image_path TEXT,
    is_available INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
)
""")

# ============================================
# ORDERS TABLE - Order records
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    shop_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    delivery_address TEXT,
    delivery_type TEXT NOT NULL,
    payment_type TEXT NOT NULL,
    total_amount REAL NOT NULL,
    payment_status TEXT DEFAULT 'Pending',
    payment_screenshot_path TEXT,
    order_status TEXT DEFAULT 'Placed',
    delivery_confirmed INTEGER DEFAULT 0,
    delivery_confirmed_at TIMESTAMP,
    delivery_boy_name TEXT,
    delivery_boy_phone TEXT,
    current_location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (shop_id) REFERENCES shops(id)
)
""")

# ============================================
# ORDER_ITEMS TABLE - Items in each order
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    food_item_id INTEGER,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id)
)
""")

# ============================================
# ORDER_STATUS_HISTORY TABLE - Track status changes
# ============================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    updated_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
)
""")

conn.commit()

# Insert default admin if not exists
cursor.execute("SELECT id FROM admin WHERE username = 'admin'")
if not cursor.fetchone():
    from werkzeug.security import generate_password_hash
    admin_password = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO admin (username, password, email) 
        VALUES (?, ?, ?)
    """, ('admin', admin_password, 'mdazhark735@gmail.com'))
    conn.commit()
    print("Default admin created: username='admin', password='admin123', email='mdazhark735@gmail.com'")

# Insert default shopkeeper and shop if not exists
cursor.execute("SELECT id FROM shopkeepers WHERE username = 'demo_shop'")
if not cursor.fetchone():
    from werkzeug.security import generate_password_hash
    shopkeeper_password = generate_password_hash('shop123')
    cursor.execute("""
        INSERT INTO shopkeepers (username, password, email, phone) 
        VALUES (?, ?, ?, ?)
    """, ('demo_shop', shopkeeper_password, 'shop@lpufood.com', '9876543210'))
    shopkeeper_id = cursor.lastrowid
    
    # Create shop for this shopkeeper
    cursor.execute("""
        INSERT INTO shops (shopkeeper_id, name, description, location, phone, email, delivery_available, delivery_charge) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (shopkeeper_id, 'LPU Mess A', 'Best food in LPU campus', 'Block 32, Near Academic Block', '9876543210', 'shop@lpufood.com', 1, 20))
    shop_id = cursor.lastrowid
    
    # Add sample food items
    sample_items = [
        ('Paneer Butter Masala', 'Creamy paneer curry with rich tomato gravy', 120, 'North Indian'),
        ('Veg Biryani', 'Aromatic rice with mixed vegetables', 100, 'Rice'),
        ('Chole Bhature', 'Spicy chickpeas with fried bread', 80, 'North Indian'),
        ('Masala Dosa', 'Crispy rice crepe with potato filling', 90, 'South Indian'),
        ('Cold Coffee', 'Refreshing cold coffee with ice cream', 60, 'Beverages'),
    ]
    
    for name, desc, price, category in sample_items:
        cursor.execute("""
            INSERT INTO food_items (shop_id, name, description, price, category) 
            VALUES (?, ?, ?, ?, ?)
        """, (shop_id, name, desc, price, category))
    
    conn.commit()
    print("Default shopkeeper created: username='demo_shop', password='shop123'")
    print("Default shop created: LPU Mess A with 5 menu items")

conn.close()

print("Database tables created successfully")
print("Tables created: users, admin, shopkeepers, shops, food_items, orders, order_items, order_status_history")
