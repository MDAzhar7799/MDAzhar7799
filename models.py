"""
Database Models and Operations for LPU Food Ordering System
"""
import os
import sqlite3
import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

if os.environ.get('VERCEL'):
    DATABASE = "/tmp/lpu.db"
else:
    DATABASE = "instance/lpu.db"

# Dynamic psycopg2 import for PostgreSQL support
DATABASE_URL = os.environ.get('DATABASE_URL')
psycopg2 = None
DictCursor = None
pg_pool = None
if DATABASE_URL:
    try:
        import psycopg2
        from psycopg2.extras import DictCursor
        from psycopg2 import pool
    except ImportError:
        pass


class PGCursorWrapper:
    """Wrapper to make PostgreSQL cursors behave exactly like sqlite3 cursors"""
    def __init__(self, cur):
        self.cur = cur
        self.lastrowid = None

    def execute(self, query, params=None):
        import re
        # Translate sqlite3 query placeholders (?) to PostgreSQL
        query_pg = query.replace('?', '%s')
        query_pg = query_pg.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        
        # Translate DATE(...) dynamically to PostgreSQL compatibility
        def replace_date(match):
            val = match.group(1).strip()
            if val.lower() in ["'now'", '"now"']:
                return "CURRENT_DATE"
            return f"({val})::date"
            
        query_pg = re.sub(r"\bDATE\(\s*([^)]+)\)", replace_date, query_pg)
        
        # Translate strftime(...) dynamically to PostgreSQL to_char
        def replace_strftime(match):
            fmt = match.group(1)
            val = match.group(2).strip()
            pg_fmt = fmt.replace('%Y', 'YYYY').replace('%m', 'MM').replace('%d', 'DD')
            if val.lower() in ["'now'", '"now"']:
                val = "CURRENT_TIMESTAMP"
            return f"to_char({val}, '{pg_fmt}')"

        query_pg = re.sub(r"strftime\(\s*['\"]([^'\"]+)['\"]\s*,\s*([^)]+)\)", replace_strftime, query_pg)
        
        is_insert = query_pg.strip().upper().startswith('INSERT')
        
        if is_insert:
            if 'RETURNING' not in query_pg.upper():
                query_pg = query_pg.strip()
                if query_pg.endswith(';'):
                    query_pg = query_pg[:-1]
                query_pg += " RETURNING id"
                
            if params:
                self.cur.execute(query_pg, params)
            else:
                self.cur.execute(query_pg)
                
            try:
                row = self.cur.fetchone()
                self.lastrowid = row[0] if row else None
            except Exception:
                self.lastrowid = None
        else:
            if params:
                self.cur.execute(query_pg, params)
            else:
                self.cur.execute(query_pg)
            
        return self

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def close(self):
        self.cur.close()


class PGConnectionWrapper:
    """Wrapper to make PostgreSQL connections behave exactly like sqlite3 Row-based connections"""
    def __init__(self, pg_conn, pool_ref=None):
        self.pg_conn = pg_conn
        self.pool_ref = pool_ref

    def cursor(self):
        cursor = self.pg_conn.cursor(cursor_factory=DictCursor)
        return PGCursorWrapper(cursor)

    def execute(self, query, params=None):
        cur_wrapper = self.cursor()
        cur_wrapper.execute(query, params)
        return cur_wrapper

    def commit(self):
        self.pg_conn.commit()

    def rollback(self):
        self.pg_conn.rollback()

    def close(self):
        if self.pool_ref:
            try:
                self.pool_ref.putconn(self.pg_conn)
            except Exception:
                self.pg_conn.close()
        else:
            self.pg_conn.close()


def get_db_connection():
    """Get database connection - dynamically supports SQLite locally and pooled PostgreSQL in production"""
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url and (db_url.startswith('postgres://') or db_url.startswith('postgresql://')):
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
        if psycopg2:
            global pg_pool
            if not pg_pool:
                pg_pool = pool.SimpleConnectionPool(1, 20, db_url)
            conn = pg_pool.getconn()
            return PGConnectionWrapper(conn, pg_pool)
        else:
            raise RuntimeError("psycopg2 package is missing but DATABASE_URL is set! Please install psycopg2-binary.")
            
    conn = sqlite3.connect(DATABASE, timeout=20, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Mapped IntegrityError class list to support both database engines dynamically
def get_db_integrity_errors():
    errors = [sqlite3.IntegrityError]
    if psycopg2:
        errors.append(psycopg2.IntegrityError)
    return tuple(errors)


# ============================================
# USER OPERATIONS
# ============================================

class User:
    @staticmethod
    def create(name, email, password, phone=None, address=None):
        """Create new user"""
        conn = get_db_connection()
        try:
            hashed_password = generate_password_hash(password)
            cursor = conn.execute(
                """INSERT INTO users (name, email, password, phone, address) 
                   VALUES (?, ?, ?, ?, ?)""",
                (name, email, hashed_password, phone, address)
            )
            conn.commit()
            return cursor.lastrowid
        except get_db_integrity_errors():
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email,)
        ).fetchone()
        conn.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        return check_password_hash(user['password'], password)


# ============================================
# ADMIN OPERATIONS
# ============================================

class Admin:
    @staticmethod
    def get_by_username(username):
        """Get admin by username"""
        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        return admin

    @staticmethod
    def get_by_id(admin_id):
        """Get admin by ID"""
        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM admin WHERE id = ?",
            (admin_id,)
        ).fetchone()
        conn.close()
        return admin

    @staticmethod
    def verify_password(admin, password):
        """Verify admin password"""
        return check_password_hash(admin['password'], password)

    @staticmethod
    def update(admin_id, **kwargs):
        """Update admin details"""
        conn = get_db_connection()
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key == 'password' and value:
                fields.append("password = ?")
                values.append(generate_password_hash(value))
            elif key in ['username', 'email']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return True
            
        values.append(admin_id)
        query = f"UPDATE admin SET {', '.join(fields)} WHERE id = ?"
        try:
            conn.execute(query, values)
            conn.commit()
            return True
        except get_db_integrity_errors():
            return False
        finally:
            conn.close()


# ============================================
# SHOPKEEPER OPERATIONS
# ============================================

class Shopkeeper:
    @staticmethod
    def create(username, password, email=None, phone=None):
        """Create new shopkeeper (by admin only)"""
        conn = get_db_connection()
        try:
            hashed_password = generate_password_hash(password)
            cursor = conn.execute(
                """INSERT INTO shopkeepers (username, password, email, phone) 
                   VALUES (?, ?, ?, ?)""",
                (username, hashed_password, email, phone)
            )
            conn.commit()
            return cursor.lastrowid
        except get_db_integrity_errors():
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """Get shopkeeper by username"""
        conn = get_db_connection()
        shopkeeper = conn.execute(
            "SELECT * FROM shopkeepers WHERE username = ? AND is_active = 1",
            (username,)
        ).fetchone()
        conn.close()
        return shopkeeper

    @staticmethod
    def get_by_id(shopkeeper_id):
        """Get shopkeeper by ID"""
        conn = get_db_connection()
        shopkeeper = conn.execute(
            "SELECT * FROM shopkeepers WHERE id = ?",
            (shopkeeper_id,)
        ).fetchone()
        conn.close()
        return shopkeeper

    @staticmethod
    def get_all():
        """Get all shopkeepers"""
        conn = get_db_connection()
        shopkeepers = conn.execute(
            "SELECT * FROM shopkeepers ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return shopkeepers

    @staticmethod
    def delete(shopkeeper_id):
        """Delete shopkeeper permanently"""
        conn = get_db_connection()
        conn.execute("DELETE FROM shopkeepers WHERE id = ?", (shopkeeper_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def verify_password(shopkeeper, password):
        """Verify shopkeeper password"""
        return check_password_hash(shopkeeper['password'], password)

    @staticmethod
    def update(shopkeeper_id, **kwargs):
        """Update shopkeeper details"""
        conn = get_db_connection()
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key == 'password' and value:
                fields.append("password = ?")
                values.append(generate_password_hash(value))
            elif key in ['email', 'phone']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return
            
        values.append(shopkeeper_id)
        query = f"UPDATE shopkeepers SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()


# ============================================
# SHOP OPERATIONS
# ============================================

class Shop:
    @staticmethod
    def create(shopkeeper_id, name, description=None, location=None, 
               phone=None, email=None, logo_path=None, delivery_available=1, delivery_charge=20):
        """Create new shop"""
        conn = get_db_connection()
        cursor = conn.execute(
            """INSERT INTO shops (shopkeeper_id, name, description, location, 
                phone, email, logo_path, delivery_available, delivery_charge) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (shopkeeper_id, name, description, location, phone, email, 
             logo_path, delivery_available, delivery_charge)
        )
        conn.commit()
        shop_id = cursor.lastrowid
        conn.close()
        return shop_id

    @staticmethod
    def get_by_id(shop_id):
        """Get shop by ID"""
        conn = get_db_connection()
        shop = conn.execute(
            """SELECT s.*, sk.username as shopkeeper_username, sk.email as shopkeeper_email
               FROM shops s 
               JOIN shopkeepers sk ON s.shopkeeper_id = sk.id 
               WHERE s.id = ? AND s.is_active = 1""",
            (shop_id,)
        ).fetchone()
        conn.close()
        return shop

    @staticmethod
    def get_by_shopkeeper(shopkeeper_id):
        """Get shop by shopkeeper ID"""
        conn = get_db_connection()
        shop = conn.execute(
            "SELECT * FROM shops WHERE shopkeeper_id = ? AND is_active = 1",
            (shopkeeper_id,)
        ).fetchone()
        conn.close()
        return shop

    @staticmethod
    def get_all(active_only=True):
        """Get all shops"""
        conn = get_db_connection()
        if active_only:
            shops = conn.execute(
                """SELECT s.*, sk.username as shopkeeper_name 
                   FROM shops s 
                   JOIN shopkeepers sk ON s.shopkeeper_id = sk.id 
                   WHERE s.is_active = 1 ORDER BY s.created_at DESC"""
            ).fetchall()
        else:
            shops = conn.execute(
                """SELECT s.*, sk.username as shopkeeper_name 
                   FROM shops s 
                   JOIN shopkeepers sk ON s.shopkeeper_id = sk.id 
                   ORDER BY s.created_at DESC"""
            ).fetchall()
        conn.close()
        return shops

    @staticmethod
    def update(shop_id, **kwargs):
        """Update shop details"""
        conn = get_db_connection()
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(shop_id)
        
        query = f"UPDATE shops SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()

    @staticmethod
    def update_qr_code(shop_id, qr_code_path, upi_id):
        """Update shop QR code"""
        conn = get_db_connection()
        conn.execute(
            "UPDATE shops SET qr_code_path = ?, upi_id = ? WHERE id = ?",
            (qr_code_path, upi_id, shop_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(shop_id):
        """Delete shop (soft delete)"""
        conn = get_db_connection()
        conn.execute("UPDATE shops SET is_active = 0 WHERE id = ?", (shop_id,))
        conn.commit()
        conn.close()


# ============================================
# FOOD ITEM OPERATIONS
# ============================================

class FoodItem:
    @staticmethod
    def create(shop_id, name, price, description=None, category=None, image_path=None):
        """Create new food item"""
        conn = get_db_connection()
        cursor = conn.execute(
            """INSERT INTO food_items (shop_id, name, description, price, category, image_path) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (shop_id, name, description, price, category, image_path)
        )
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id

    @staticmethod
    def get_by_id(item_id):
        """Get food item by ID"""
        conn = get_db_connection()
        item = conn.execute(
            "SELECT * FROM food_items WHERE id = ?",
            (item_id,)
        ).fetchone()
        conn.close()
        return item

    @staticmethod
    def get_by_shop(shop_id, available_only=True):
        """Get all food items for a shop"""
        conn = get_db_connection()
        if available_only:
            items = conn.execute(
                """SELECT * FROM food_items 
                   WHERE shop_id = ? AND is_available = 1 
                   ORDER BY category, name""",
                (shop_id,)
            ).fetchall()
        else:
            items = conn.execute(
                """SELECT * FROM food_items 
                   WHERE shop_id = ? 
                   ORDER BY category, name""",
                (shop_id,)
            ).fetchall()
        conn.close()
        return items

    @staticmethod
    def update(item_id, **kwargs):
        """Update food item"""
        conn = get_db_connection()
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(item_id)
        
        query = f"UPDATE food_items SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()

    @staticmethod
    def delete(item_id):
        """Delete food item"""
        conn = get_db_connection()
        conn.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()


# ============================================
# ORDER OPERATIONS
# ============================================

def generate_order_number():
    """Generate unique order number without LPU prefix"""
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"FEX{timestamp}{random_str}"


class Order:
    @staticmethod
    def create(user_id, shop_id, customer_name, customer_phone, delivery_address,
               delivery_type, payment_type, total_amount):
        """Create new order"""
        conn = get_db_connection()
        order_number = generate_order_number()
        
        cursor = conn.execute(
            """INSERT INTO orders (order_number, user_id, shop_id, customer_name, 
                customer_phone, delivery_address, delivery_type, payment_type, total_amount) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_number, user_id, shop_id, customer_name, customer_phone,
             delivery_address, delivery_type, payment_type, total_amount)
        )
        order_id = cursor.lastrowid
        
        # Add status history
        conn.execute(
            """INSERT INTO order_status_history (order_id, status, notes, updated_by) 
               VALUES (?, ?, ?, ?)""",
            (order_id, 'Placed', 'Order placed successfully', 'System')
        )
        
        conn.commit()
        conn.close()
        return order_id, order_number

    @staticmethod
    def get_by_id(order_id):
        """Get order by ID"""
        conn = get_db_connection()
        order = conn.execute(
            """SELECT o.*, s.name as shop_name, s.phone as shop_phone, s.location as shop_location,
                      u.name as customer_name, u.phone as customer_phone, u.email as customer_email,
                      h.notes as cancellation_reason, h.updated_by as status_updated_by
               FROM orders o 
               JOIN shops s ON o.shop_id = s.id 
               JOIN users u ON o.user_id = u.id
               LEFT JOIN (
                   SELECT order_id, notes, updated_by,
                          ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) as rn
                   FROM order_status_history
               ) h ON o.id = h.order_id AND h.rn = 1
               WHERE o.id = ?""",
            (order_id,)
        ).fetchone()
        conn.close()
        return order

    @staticmethod
    def get_by_order_number(order_number):
        """Get order by order number"""
        conn = get_db_connection()
        order = conn.execute(
            """SELECT o.*, s.name as shop_name, s.phone as shop_phone, s.location as shop_location,
                      h.notes as cancellation_reason, h.updated_by as status_updated_by
               FROM orders o 
               JOIN shops s ON o.shop_id = s.id 
               LEFT JOIN (
                   SELECT order_id, notes, updated_by,
                          ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) as rn
                   FROM order_status_history
               ) h ON o.id = h.order_id AND h.rn = 1
               WHERE o.order_number = ?""",
            (order_number,)
        ).fetchone()
        conn.close()
        return order

    @staticmethod
    def get_by_user(user_id):
        """Get all orders for a user"""
        conn = get_db_connection()
        orders = conn.execute(
            """SELECT o.*, s.name as shop_name,
                      h.notes as cancellation_reason, h.updated_by as status_updated_by
               FROM orders o 
               JOIN shops s ON o.shop_id = s.id 
               LEFT JOIN (
                   SELECT order_id, notes, updated_by,
                          ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) as rn
                   FROM order_status_history
               ) h ON o.id = h.order_id AND h.rn = 1
               WHERE o.user_id = ? 
               ORDER BY o.created_at DESC""",
            (user_id,)
        ).fetchall()
        conn.close()
        return orders

    @staticmethod
    def get_by_shop(shop_id):
        """Get all orders for a shop"""
        conn = get_db_connection()
        orders = conn.execute(
            """SELECT o.*, u.name as customer_name, u.phone as customer_phone
               FROM orders o 
               JOIN users u ON o.user_id = u.id 
               LEFT JOIN (
                   SELECT order_id, updated_by,
                          ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) as rn
                   FROM order_status_history
               ) h ON o.id = h.order_id AND h.rn = 1
               WHERE o.shop_id = ? 
               ORDER BY o.created_at DESC""",
            (shop_id,)
        ).fetchall()
        conn.close()
        return orders

    @staticmethod
    def get_all():
        """Get all orders (admin)"""
        conn = get_db_connection()
        orders = conn.execute(
            """SELECT o.*, s.name as shop_name, u.name as customer_name, u.email as customer_email, u.phone as customer_phone
               FROM orders o 
               JOIN shops s ON o.shop_id = s.id 
               JOIN users u ON o.user_id = u.id 
               ORDER BY o.created_at DESC"""
        ).fetchall()
        conn.close()
        return orders

    @staticmethod
    def get_all_by_shop(shop_id):
        """Get all orders for a shop (admin) including all statuses"""
        conn = get_db_connection()
        orders = conn.execute(
            """SELECT o.*, u.name as customer_name, u.email as customer_email, u.phone as customer_phone
               FROM orders o 
               JOIN users u ON o.user_id = u.id 
               WHERE o.shop_id = ? 
               ORDER BY o.created_at DESC""",
            (shop_id,)
        ).fetchall()
        conn.close()
        return orders

    @staticmethod
    def update_status(order_id, status, notes=None, updated_by='System', delivery_info=None):
        """Update order status and optionally delivery person info in ONE transaction"""
        conn = get_db_connection()
        try:
            # Update main order status
            conn.execute(
                "UPDATE orders SET order_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, order_id)
            )
            
            # If delivery info provided, update it too
            if delivery_info:
                conn.execute(
                    """UPDATE orders SET 
                       delivery_boy_name = ?, 
                       delivery_boy_phone = ?, 
                       current_location = ?
                       WHERE id = ?""",
                    (delivery_info['name'], delivery_info['phone'], delivery_info['location'], order_id)
                )
            
            # Add to history
            conn.execute(
                "INSERT INTO order_status_history (order_id, status, notes, updated_by) VALUES (?, ?, ?, ?)",
                (order_id, status, notes, updated_by)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_payment_screenshot(order_id, screenshot_path):
        """Update payment screenshot"""
        conn = get_db_connection()
        conn.execute(
            """UPDATE orders SET payment_screenshot_path = ?, payment_status = 'Pending Verification' 
               WHERE id = ?""",
            (screenshot_path, order_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def set_notified(order_id):
        """Mark order as notified for pickup"""
        conn = get_db_connection()
        conn.execute(
            "UPDATE orders SET is_notified = 1 WHERE id = ?",
            (order_id,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def verify_payment(order_id, verified=True):
        """Verify payment"""
        conn = get_db_connection()
        status = 'Paid' if verified else 'Rejected'
        conn.execute(
            "UPDATE orders SET payment_status = ? WHERE id = ?",
            (status, order_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def confirm_delivery(order_id):
        """Confirm order delivery by customer - updates only order status, not payment"""
        conn = get_db_connection()
        conn.execute(
            """UPDATE orders SET 
                delivery_confirmed = 1, 
                delivery_confirmed_at = CURRENT_TIMESTAMP,
                order_status = 'Delivered'
               WHERE id = ?""",
            (order_id,)
        )
        conn.execute(
            """INSERT INTO order_status_history (order_id, status, notes, updated_by) 
               VALUES (?, ?, ?, ?)""",
            (order_id, 'Delivered', 'Order delivered and confirmed by customer. Payment verification pending.', 'Customer')
        )
        conn.commit()
        conn.close()


class OrderItem:
    @staticmethod
    def create(order_id, food_item_id, item_name, quantity, price):
        """Create order item"""
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO order_items (order_id, food_item_id, item_name, quantity, price) 
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, food_item_id, item_name, quantity, price)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_order(order_id):
        """Get all items for an order with images"""
        conn = get_db_connection()
        items = conn.execute(
            """SELECT oi.*, fi.image_path 
               FROM order_items oi 
               LEFT JOIN food_items fi ON oi.food_item_id = fi.id 
               WHERE oi.order_id = ?""",
            (order_id,)
        ).fetchall()
        conn.close()
        return items


# ============================================
# STATISTICS
# ============================================

class Statistics:
    @staticmethod
    def get_counts():
        """Get dashboard counts"""
        conn = get_db_connection()
        stats = {}
        
        # Total orders (Excluding User Cancelled)
        result = conn.execute("SELECT COUNT(*) as count FROM orders WHERE order_status != 'User Cancelled'").fetchone()
        stats['total_orders'] = result['count']
        
        # Active shops
        result = conn.execute(
            "SELECT COUNT(*) as count FROM shops WHERE is_active = 1"
        ).fetchone()
        stats['active_shops'] = result['count']
        
        # Total users
        result = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE is_active = 1"
        ).fetchone()
        stats['total_users'] = result['count']
        
        # Total shopkeepers
        result = conn.execute(
            "SELECT COUNT(*) as count FROM shopkeepers WHERE is_active = 1"
        ).fetchone()
        stats['total_shopkeepers'] = result['count']
        
        # Today's orders (Excluding User Cancelled)
        result = conn.execute(
            """SELECT COUNT(*) as count FROM orders 
               WHERE DATE(created_at) = DATE('now') 
               AND order_status != 'User Cancelled'"""
        ).fetchone()
        stats['today_orders'] = result['count']
        
        conn.close()
        return stats
