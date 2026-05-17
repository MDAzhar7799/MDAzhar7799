import os
from models import get_db_connection

# Ensure instance directory exists (bypass on Vercel read-only system)
if not os.environ.get('VERCEL'):
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

# Insert or update default admins to match local database passwords exactly
admins_to_seed = [
    {
        'username': 'Azhar',
        'password_hash': 'pbkdf2:sha256:600000$o5kU3VOpSS0jenON$0daaea727e3459eaab41570b6ebe553eb38416fa7caea0d53084ca593fbf1fd5',
        'email': 'mdazhark735@gmail.com'
    },
    {
        'username': 'admin',
        'password_hash': 'pbkdf2:sha256:600000$4JJsbQJLNKBauQwS$140ac9b4295b6cfa792aed64f9e0e98a709c16db05b3ec540016b0caa6beb0c6',
        'email': 'mdazhark735@gmail.com'
    }
]

for adm in admins_to_seed:
    cursor.execute("SELECT id FROM admin WHERE username = ?", (adm['username'],))
    row = cursor.fetchone()
    if not row:
        cursor.execute("""
            INSERT INTO admin (username, password, email) 
            VALUES (?, ?, ?)
        """, (adm['username'], adm['password_hash'], adm['email']))
        print(f"Seeded admin: {adm['username']}")
    else:
        cursor.execute("UPDATE admin SET password = ?, email = ? WHERE username = ?", (adm['password_hash'], adm['email'], adm['username']))
        print(f"Updated admin password/email: {adm['username']}")
conn.commit()

# Insert or update default shopkeepers and shops to match local database passwords exactly
shopkeepers_to_seed = [
    {
        'username': 'demo_shop',
        'password_hash': 'pbkdf2:sha256:600000$y0PoHXcEaSrL4t0n$671c6b9f70720b6cc3e7c18795a4d17b2f4236d46e81ff209d1e6c8a8fce029c',
        'email': 'shop@lpufood.com',
        'phone': '9876543210',
        'shop': {
            'name': 'LPU Block 27',
            'description': 'Best food in LPU campus',
            'location': 'LPU 27',
            'phone': '9876543210',
            'email': 'shop@lpufood.com',
            'delivery_available': 1,
            'delivery_charge': 20.0,
            'is_active': 1,
            'logo_path': 'uploads/lpu_mess_logo.png',
            'items': [
                ('Paneer Butter Masala', 'Creamy paneer curry with rich tomato gravy', 120.0, 'North Indian', None),
                ('Veg Biryani', 'Aromatic rice with mixed vegetables', 100.0, 'Rice', None),
                ('Chole Bhature', 'Spicy chickpeas with fried bread', 80.0, 'North Indian', None),
                ('Masala Dosa', 'Crispy rice crepe with potato filling', 90.0, 'South Indian', None),
                ('Cold Coffee', 'Refreshing cold coffee with ice cream', 60.0, 'Beverages', 'uploads/food_images/food_1_20260427_214413_Affogato.png'),
                ('Dam Biryani', 'kashmir', 100.0, 'special', 'uploads/food_images/food_1_20260309_000156_dosa.png')
            ]
        }
    },
    {
        'username': 'lawget',
        'password_hash': 'pbkdf2:sha256:600000$uh3WZsdyPKkrTVNG$616e9d6b35d0f401c45d3a33918d5226a3c74f9b530c0fcf0903ce22e7324c86',
        'email': 'lawget7799@gmail.com',
        'phone': '1234567891',
        'shop': {
            'name': 'Lawget-Pizza',
            'description': 'Delicious pizzas, garlic bread, and classic Italian sides at LawGate',
            'location': 'Classic',
            'phone': '1234567891',
            'email': 'lawget7799@gmail.com',
            'upi_id': 'mdazhar7799',
            'qr_code_path': 'uploads/qr_codes/shop_3_20260503_185053_50_day_leetcode.png',
            'delivery_available': 1,
            'delivery_charge': 20.0,
            'is_active': 1,
            'logo_path': 'uploads/lawgate_shop_logo.png',
            'items': [
                ('Dam Biryani', 'kashmir', 150.0, 'North', 'uploads/food_images/food_3_20260308_232352_butter_paneer_masala.png'),
                ('Gulab jamun', 'kashmir', 10.0, 'special', 'uploads/food_images/food_3_20260404_184039_Screenshot_2026-04-04_184008.png'),
                ('Coffee', 'Special Drinks', 10.0, 'Drinks', 'uploads/food_images/food_3_20260516_212037_17789465931747103525050938417352.jpg')
            ]
        }
    },
    {
        'username': 'new',
        'password_hash': 'pbkdf2:sha256:600000$ABHyLRuQI12LR3ic$d73fa33ef7c993adf17d49a20bfb2a571e0925448f5e55351b87f7d70ca10eeb',
        'email': 'new1234@gmail.com',
        'phone': '9988776655',
        'shop': {
            'name': 'green',
            'description': 'Fresh salads, green bowls, and organic juices',
            'location': 'pizza',
            'phone': '9988776655',
            'email': 'new1234@gmail.com',
            'delivery_available': 1,
            'delivery_charge': 20.0,
            'is_active': 0,
            'logo_path': None,
            'items': [
                ('coffee', 'Fresh brewed hot coffee', 10.0, 'Drinks', 'uploads/food_images/food_4_20260507_212139_Cortado.png')
            ]
        }
    }
]

for sk in shopkeepers_to_seed:
    cursor.execute("SELECT id FROM shopkeepers WHERE username = ?", (sk['username'],))
    row = cursor.fetchone()
    if not row:
        cursor.execute("""
            INSERT INTO shopkeepers (username, password, email, phone) 
            VALUES (?, ?, ?, ?)
        """, (sk['username'], sk['password_hash'], sk['email'], sk['phone']))
        shopkeeper_id = cursor.lastrowid
        
        # Create shop
        shop = sk['shop']
        cursor.execute("""
            INSERT INTO shops (shopkeeper_id, name, description, location, phone, email, upi_id, qr_code_path, delivery_available, delivery_charge, is_active, logo_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shopkeeper_id, 
            shop['name'], 
            shop['description'], 
            shop['location'], 
            shop['phone'], 
            shop['email'], 
            shop.get('upi_id'), 
            shop.get('qr_code_path'), 
            shop['delivery_available'], 
            shop['delivery_charge'], 
            shop['is_active'], 
            shop['logo_path']
        ))
        shop_id = cursor.lastrowid
        
        # Add food items
        for name, desc, price, cat, img in shop['items']:
            cursor.execute("""
                INSERT INTO food_items (shop_id, name, description, price, category, image_path) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (shop_id, name, desc, price, cat, img))
            
        print(f"Seeded shopkeeper: {sk['username']} with shop: {shop['name']}")
    else:
        # Update shopkeeper password dynamically to match local db password hash
        cursor.execute("UPDATE shopkeepers SET password = ?, email = ?, phone = ? WHERE username = ?", (sk['password_hash'], sk['email'], sk['phone'], sk['username']))
        print(f"Updated shopkeeper password: {sk['username']}")

conn.commit()
conn.close()

print("Database tables created and fully seeded successfully")
print("Tables populated: users, admin, shopkeepers, shops, food_items")
