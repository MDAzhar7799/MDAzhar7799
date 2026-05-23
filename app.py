"""
LPU Food Ordering System - Main Flask Application
Real food ordering platform with multi-shopkeeper support and secure UPI payments
"""
import os
import secrets
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# Load .env file if present (for local dev + production config)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # python-dotenv optional; use OS env vars directly in production

import cloudinary
import cloudinary.uploader

# Cloudinary CDN Configuration with dynamic environment variable checking
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
if CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)
else:
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models import (
    User, Admin, Shopkeeper, Shop, FoodItem, Order, OrderItem, 
    Statistics, get_db_connection
)

# Initialize Flask app
app = Flask(__name__)

# Initialize database schema globally (required for Serverless environments like Vercel)
import schema_init

# ─── PRODUCTION-GRADE CONFIG ─────────────────────────────────
# Stable secret key from env (fallback for dev only)
app.secret_key = os.environ.get('SECRET_KEY', 'Azhar-FoodExpress-SuperSecret-2026-LPU-LawGate-xK9mP2qR')

# Session security settings
app.config['SESSION_COOKIE_SECURE'] = False      # Set True when behind HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Fast2SMS API key (loaded from .env or hardcoded fallback)
FAST2SMS_API_KEY = os.environ.get(
    'FAST2SMS_API_KEY',
    'kU38MfPKnWHJYb46wpGxByaevOFSo1R7jcgCudmZNlEiDhQs0XxbPQmNT6hFta5sO7Egcr1lXyWH2ivC'
)

# File upload paths (dynamically adapt to /tmp in read-only serverless environments)
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
    QR_CODE_FOLDER = os.path.join(UPLOAD_FOLDER, 'qr_codes')
    PAYMENT_FOLDER = os.path.join(UPLOAD_FOLDER, 'payment_screenshots')
    FOOD_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'food_images')
    SHOP_LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, 'shop_logos')
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    QR_CODE_FOLDER = os.path.join(UPLOAD_FOLDER, 'qr_codes')
    PAYMENT_FOLDER = os.path.join(UPLOAD_FOLDER, 'payment_screenshots')
    FOOD_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'food_images')
    SHOP_LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, 'shop_logos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB default


# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directories
os.makedirs(QR_CODE_FOLDER, exist_ok=True)
os.makedirs(PAYMENT_FOLDER, exist_ok=True)
os.makedirs(FOOD_IMAGE_FOLDER, exist_ok=True)
os.makedirs(SHOP_LOGO_FOLDER, exist_ok=True)


# SMTP Email Configuration (MailerSend)
app.config['SMTP_SERVER'] = os.environ.get('SMTP_SERVER', 'smtp.mailersend.net')
app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT', 587))
app.config['SMTP_USER'] = os.environ.get('SMTP_USER', 'MS_XwNkdY@test-68zxl273emm4j905.mlsender.net')
app.config['SMTP_PASS'] = os.environ.get('SMTP_PASS', 'mlsn.7448967837fd568925745ea11a87fb3f5cfb8b9a82f79077d3a06fa700c4c629')
app.config['SENDER_EMAIL'] = os.environ.get('SENDER_EMAIL', 'noreply@test-68zxl273emm4j905.mlsender.net')
app.config['SENDER_NAME'] = os.environ.get('SENDER_NAME', 'FoodExpress Notifications')


# ============================================
# HELPER FUNCTIONS
# ============================================

def send_email(to_email, subject, body_html):
    """Utility to send HTML emails via SMTP"""
    if not app.config['SMTP_PASS']:
        print("[EMAIL ERROR] SMTP Password/API Key not configured.")
        return False, "SMTP credentials missing"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{app.config['SENDER_NAME']} <{app.config['SENDER_EMAIL']}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body_html, 'html'))

        with smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT']) as server:
            server.starttls()
            server.login(app.config['SMTP_USER'], app.config['SMTP_PASS'])
            server.send_message(msg)
            
        print(f"[EMAIL SUCCESS] Notification sent to {to_email}")
        return True, "Email sent successfully"
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}")
        return False, str(e)

def log_user_login(email, name, user_type):
    """Log user login to file for tracking"""
    import datetime
    if os.environ.get('VERCEL'):
        log_file = '/tmp/user_logins.txt'
    else:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_logins.txt')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {user_type.upper()} LOGIN - Email: {email}, Name: {name}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[LOG ERROR] Failed to write to login log: {str(e)}")

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def login_required(f):
    """Decorator for routes that require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def shopkeeper_required(f):
    """Decorator for routes that require shopkeeper login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'shopkeeper_id' not in session:
            flash('Please login as shopkeeper to access this page', 'warning')
            return redirect(url_for('shopkeeper_login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for routes that require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login as admin to access this page', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def add_header(response):
    """Disable caching for all dynamic html requests to prevent stale mobile views"""
    if response.headers.get('Content-Type', '').startswith('text/html'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


@app.template_filter('dateformat')
def dateformat_filter(value, fmt='%Y-%m-%d'):
    """Jinja2 filter: safely format a date/datetime from either PostgreSQL (datetime obj) or SQLite (string).
    Usage in templates: {{ order.created_at | dateformat }}            → '2026-05-17'
                        {{ order.created_at | dateformat('%Y-%m-%d %H:%M') }} → '2026-05-17 21:00'
                        {{ order.created_at | dateformat('%m') }}      → '05'
    """
    if value is None:
        return 'N/A'
    # PostgreSQL returns a datetime object — use strftime directly
    if hasattr(value, 'strftime'):
        return value.strftime(fmt)
    # SQLite returns a string — slice by format length
    s = str(value)
    if fmt == '%Y-%m-%d':
        return s[:10]
    if fmt == '%Y-%m-%d %H:%M':
        return s[:16]
    if fmt == '%m':
        return s[5:7]
    if fmt == '%H:%M':
        return s[11:16]
    return s


@app.template_filter('img_url')
def img_url_filter(value):
    """Jinja2 filter to safely render absolute Cloudinary URLs, Base64 data, or local disk fallback paths."""
    if not value:
        return ''
    if value.startswith('http://') or value.startswith('https://') or value.startswith('data:'):
        return value
    if value.startswith('/'):
        return value
    return '/' + value


@app.context_processor
def override_url_for():
    """Context processor to intercept static/serve_upload url_for calls and return absolute Cloudinary URLs directly."""
    original_url_for = url_for
    def custom_url_for(endpoint, **values):
        if endpoint in ['static', 'serve_upload'] and 'filename' in values:
            filename = values['filename']
            if filename and (filename.startswith('http://') or filename.startswith('https://') or filename.startswith('data:')):
                return filename
        return original_url_for(endpoint, **values)
    return dict(url_for=custom_url_for)


def upload_image_to_cloud_or_disk(file, folder):
    """
    Uploads a file to Cloudinary if it is configured.
    Otherwise, saves it locally and returns the local relative path for backwards compatibility.
    """
    # Check if Cloudinary is configured
    config = cloudinary.config()
    if config.cloud_name and config.api_key and config.api_secret:
        try:
            # Upload to Cloudinary under the folder foodexpress/<subfolder>
            upload_result = cloudinary.uploader.upload(
                file,
                folder=f"foodexpress/{folder}"
            )
            secure_url = upload_result.get('secure_url')
            if secure_url:
                print(f"[CLOUDINARY SUCCESS] Uploaded to {secure_url}")
                return secure_url
        except Exception as e:
            print(f"[CLOUDINARY ERROR] Upload failed, falling back to local storage: {str(e)}")
            
    # Local disk fallback
    import datetime
    from werkzeug.utils import secure_filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{folder}_{timestamp}_{secure_filename(file.filename)}"
    
    if folder == 'qr_codes':
        target_dir = QR_CODE_FOLDER
        db_path = f"uploads/qr_codes/{filename}"
    elif folder == 'payment_screenshots':
        target_dir = PAYMENT_FOLDER
        db_path = f"uploads/payment_screenshots/{filename}"
    elif folder == 'food_images':
        target_dir = FOOD_IMAGE_FOLDER
        db_path = f"uploads/food_images/{filename}"
    elif folder == 'shop_logos':
        target_dir = SHOP_LOGO_FOLDER
        db_path = f"static/uploads/shop_logos/{filename}"
    else:
        target_dir = UPLOAD_FOLDER
        db_path = f"uploads/{filename}"
        
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, filename)
    file.save(file_path)
    print(f"[LOCAL UPLOAD] Saved locally to {db_path}")
    return db_path



# ============================================
# PUBLIC ROUTES
# ============================================

@app.route("/")
def home():
    """Home page"""
    shops = Shop.get_all(active_only=True)
    return render_template("index.html", shops=shops)


@app.route("/shops")
def shops_list():
    """List all active shops"""
    shops = Shop.get_all(active_only=True)
    return render_template("shops.html", shops=shops)


@app.route("/shop/<int:shop_id>")
def shop_menu(shop_id):
    """View shop menu"""
    shop = Shop.get_by_id(shop_id)
    if not shop:
        flash('Shop not found', 'error')
        return redirect(url_for('shops_list'))
    
    food_items = FoodItem.get_by_shop(shop_id, available_only=True)
    return render_template("shop_menu.html", shop=shop, food_items=food_items)


# ============================================
# USER AUTHENTICATION ROUTES
# ============================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        if not all([name, email, password]):
            flash('Please fill in all required fields', 'error')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template("register.html")
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template("register.html")
        
        # Check if email exists
        if User.get_by_email(email):
            flash('Email already registered', 'error')
            return render_template("register.html")
        
        # Create user
        user_id = User.create(name, email, password, phone, address)
        if user_id:
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again', 'error')
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.get_by_email(email)
        if user and User.verify_password(user, password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session.permanent = True  # Make session persistent
            
            # Store login info in file for tracking
            log_user_login(user['email'], user['name'], 'customer')
            
            flash(f'Welcome back, {user["name"]}! Login successful.', 'success')
            
            # Redirect to intended page or home
            print(f"Debug: User {user['email']} logged in successfully.")
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            print(f"Debug: Failed login attempt for {email}")
            flash('Invalid email or password', 'error')
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout"""
    session.pop('_flashes', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    """User profile page"""
    user = User.get_by_id(session['user_id'])
    orders = Order.get_by_user(session['user_id'])
    return render_template("profile.html", user=user, orders=orders)


# ============================================
# SHOPKEEPER AUTHENTICATION ROUTES
# ============================================

@app.route("/shopkeeper/login", methods=["GET", "POST"])
def shopkeeper_login():
    """Shopkeeper login"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        shopkeeper = Shopkeeper.get_by_username(username)
        if shopkeeper and Shopkeeper.verify_password(shopkeeper, password):
            session['shopkeeper_id'] = shopkeeper['id']
            session['shopkeeper_username'] = shopkeeper['username']
            session.permanent = True
            
            # Get shop info
            shop = Shop.get_by_shopkeeper(shopkeeper['id'])
            if shop:
                session['shop_id'] = shop['id']
            
            # Log login
            shopkeeper_email = shopkeeper['email'] if 'email' in shopkeeper.keys() else 'N/A'
            log_user_login(shopkeeper['username'], shopkeeper_email, 'shopkeeper')
            
            flash(f'Welcome back, {shopkeeper["username"]}! Login successful.', 'success')
            return redirect(url_for('shopkeeper_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("shopkeeper_login.html")


@app.route("/shopkeeper/logout")
def shopkeeper_logout():
    """Shopkeeper logout"""
    session.pop('_flashes', None)
    session.pop('shopkeeper_id', None)
    session.pop('shopkeeper_username', None)
    session.pop('shop_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('shopkeeper_login'))


# ============================================
# SHOPKEEPER DASHBOARD ROUTES
# ============================================

@app.route("/shopkeeper/profile", methods=["GET", "POST"])
@shopkeeper_required
def shopkeeper_profile():
    """Shopkeeper profile page"""
    shopkeeper_id = session['shopkeeper_id']
    shopkeeper = Shopkeeper.get_by_id(shopkeeper_id)
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    stats = {
        'total_orders': 0,
        'total_menu_items': 0,
        'pending_orders': 0
    }
    
    if request.method == "POST":
        # Handle profile update form
        shop_name = request.form.get('shop_name', '').strip()
        shop_location = request.form.get('location', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        # 1. Update Shop Name and Location if changed
        if shop:
            update_shop_fields = {}
            if shop_name: update_shop_fields['name'] = shop_name
            if shop_location: update_shop_fields['location'] = shop_location
            if update_shop_fields:
                Shop.update(shop['id'], **update_shop_fields)
            
        # 2. Update Shopkeeper details
        update_data = {}
        if email: update_data['email'] = email
        if phone: update_data['phone'] = phone
        if password: update_data['password'] = password
        
        if update_data:
            Shopkeeper.update(shopkeeper_id, **update_data)
            
        if shop_name or shop_location or update_data:
            if password:
                flash('New password created successfully!', 'success')
            else:
                flash('Profile updated successfully!', 'success')
            return redirect(url_for('shopkeeper_profile'))

        # Update shop logo (separate logic if needed, but current form uses standard POST)
        if 'logo' in request.files:
            file = request.files['logo']
            if file.filename != '' and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                logo_path = upload_image_to_cloud_or_disk(file, 'shop_logos')
                Shop.update(shop['id'], logo_path=logo_path)
                flash('Shop logo updated successfully!', 'success')
                return redirect(url_for('shopkeeper_profile'))
    
    if shop:
        orders = Order.get_by_shop(shop['id'])
        food_items = FoodItem.get_by_shop(shop['id'], available_only=False)
        stats['total_orders'] = len(orders)
        stats['total_menu_items'] = len(food_items)
        stats['pending_orders'] = len([o for o in orders if o['order_status'] in ['Placed', 'Preparing']])
    
    return render_template("shopkeeper_profile.html", 
                         shopkeeper=shopkeeper, 
                         shop=shop,
                         **stats)


@app.route("/shopkeeper/dashboard")
@shopkeeper_required
def shopkeeper_dashboard():
    """Shopkeeper dashboard"""
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if not shop:
        flash('No shop assigned to your account. Please contact admin.', 'error')
        return render_template("shopkeeper_dashboard.html", shop=None)
    
    # Get shop stats
    orders = Order.get_by_shop(shop['id'])
    food_items = FoodItem.get_by_shop(shop['id'], available_only=False)
    
    # Count orders by status and payment
    pending_orders = [o for o in orders if o['order_status'] in ['Placed', 'Preparing', 'Ready', 'On The Way']]
    pending_payments = [o for o in orders if o['payment_status'] != 'Paid']
    
    return render_template(
        "shopkeeper_dashboard.html",
        shop=shop,
        orders=orders,
        food_items=food_items,
        pending_count=len(pending_orders),
        pending_payments=len(pending_payments),
        total_orders=len(orders),
        menu_items=len(food_items)
    )


@app.route("/shopkeeper/qr-code", methods=["GET", "POST"])
@shopkeeper_required
def shopkeeper_qr_code():
    """Manage shop QR code"""
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if not shop:
        flash('No shop assigned to your account', 'error')
        return redirect(url_for('shopkeeper_dashboard'))
    
    if request.method == "POST":
        upi_id = request.form.get('upi_id', '').strip()
        file = request.files.get('qr_code')
        
        # Case 1: A new QR image was uploaded
        if file and file.filename != '':
            if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                relative_path = upload_image_to_cloud_or_disk(file, 'qr_codes')
                Shop.update_qr_code(shop['id'], relative_path, upi_id)
                flash('QR Code and UPI ID updated successfully!', 'success')
            else:
                flash('Invalid file type. Please upload an image (PNG, JPG, JPEG)', 'error')
                return redirect(request.url)
        
        # Case 2: No new image — just update UPI ID
        elif upi_id:
            Shop.update(shop['id'], upi_id=upi_id)
            flash('UPI ID updated successfully!', 'success')
        
        else:
            flash('Please enter a UPI ID or upload a QR code.', 'error')
            return redirect(request.url)
        
        return redirect(url_for('shopkeeper_qr_code'))
    
    return render_template("shopkeeper_qr.html", shop=shop)


@app.route("/shopkeeper/upload_image", methods=['GET', 'POST'])
@shopkeeper_required
def shopkeeper_upload_image():
    """Route for shopkeepers to upload their shop logo/image"""
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if not shop:
        flash('Shop profile not found. Please contact admin.', 'danger')
        return redirect(url_for('shopkeeper_dashboard'))
        
    if request.method == 'POST':
        if 'shop_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['shop_image']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            logo_path = upload_image_to_cloud_or_disk(file, 'shop_logos')
            Shop.update(shop['id'], logo_path=logo_path)
            
            flash('Shop image updated successfully!', 'success')
            return redirect(url_for('shopkeeper_dashboard'))
        else:
            flash('Invalid file type. Please upload an image (png, jpg, jpeg, gif, webp).', 'danger')
            
    return render_template("shopkeeper_upload_image.html", shop=shop)


@app.route("/shopkeeper/menu", methods=["GET", "POST"])
@shopkeeper_required
def shopkeeper_menu():
    """Manage shop menu"""
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if not shop:
        flash('No shop assigned to your account', 'error')
        return redirect(url_for('shopkeeper_dashboard'))
    
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', 0)
            category = request.form.get('category', '').strip()
            
            if not name or not price:
                flash('Item name and price are required', 'error')
                return redirect(request.url)
            
            try:
                price = float(price)
            except ValueError:
                flash('Invalid price', 'error')
                return redirect(request.url)
            
            # Handle image upload to work on Vercel/Render (Cloudinary with base64 fallback)
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '' and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    config = cloudinary.config()
                    if config.cloud_name and config.api_key and config.api_secret:
                        try:
                            upload_result = cloudinary.uploader.upload(file, folder="foodexpress/food_images")
                            image_path = upload_result.get('secure_url')
                        except Exception as e:
                            print(f"[CLOUDINARY ERROR] Food image upload failed: {str(e)}")
                    
                    if not image_path:
                        import base64
                        encoded_string = base64.b64encode(file.read()).decode('utf-8')
                        mime_type = file.mimetype if file.mimetype else 'image/jpeg'
                        image_path = f"data:{mime_type};base64,{encoded_string}"
            
            FoodItem.create(shop['id'], name, price, description, category, image_path)
            flash('Food item added successfully!', 'success')
            
        elif action == 'update':
            item_id = request.form.get('item_id')
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', 0)
            category = request.form.get('category', '').strip()
            is_available = 1 if request.form.get('is_available') else 0
            
            try:
                price = float(price)
            except ValueError:
                flash('Invalid price', 'error')
                return redirect(request.url)
            
            # Handle image update
            update_data = {
                'name': name,
                'description': description,
                'price': price,
                'category': category,
                'is_available': is_available
            }
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '' and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    image_path = None
                    config = cloudinary.config()
                    if config.cloud_name and config.api_key and config.api_secret:
                        try:
                            upload_result = cloudinary.uploader.upload(file, folder="foodexpress/food_images")
                            image_path = upload_result.get('secure_url')
                        except Exception as e:
                            print(f"[CLOUDINARY ERROR] Food image update failed: {str(e)}")
                    
                    if image_path:
                        update_data['image_path'] = image_path
                    else:
                        import base64
                        encoded_string = base64.b64encode(file.read()).decode('utf-8')
                        mime_type = file.mimetype if file.mimetype else 'image/jpeg'
                        update_data['image_path'] = f"data:{mime_type};base64,{encoded_string}"
            
            FoodItem.update(item_id, **update_data)
            flash('Food item updated successfully!', 'success')
            
        elif action == 'delete':
            item_id = request.form.get('item_id')
            try:
                # Cast to int for DB compatibility
                item_id_int = int(item_id)
                print(f"DEBUG: Attempting to delete item ID: {item_id_int}")
                
                # Check if item belongs to this shop
                item = FoodItem.get_by_id(item_id_int)
                if item and item['shop_id'] == shop['id']:
                    FoodItem.delete(item_id_int)
                    flash('Food item deleted successfully!', 'success')
                    print(f"DEBUG: Success - Item {item_id_int} deleted.")
                else:
                    print(f"DEBUG ERROR: Item {item_id_int} not found or not owned by shop {shop['id']}")
                    flash('Error: You do not have permission to delete this item.', 'error')
                
                return redirect(url_for('shopkeeper_menu'))
            except Exception as e:
                print(f"DEBUG ERROR: Failed to delete item {item_id}: {str(e)}")
                flash(f'Error deleting item: {str(e)}', 'error')
                return redirect(url_for('shopkeeper_menu'))
    
    food_items_raw = FoodItem.get_by_shop(shop['id'], available_only=False)
    food_items = [dict(item) for item in food_items_raw]
    return render_template("shopkeeper_menu.html", shop=shop, food_items=food_items)


@app.route("/shopkeeper/orders")
@shopkeeper_required
def shopkeeper_orders():
    """View and manage orders"""
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if not shop:
        flash('No shop assigned to your account', 'error')
        return redirect(url_for('shopkeeper_dashboard'))
    
    orders = Order.get_by_shop(shop['id'])
    return render_template("shopkeeper_orders.html", shop=shop, orders=orders)


@app.route("/shopkeeper/order/<int:order_id>", methods=["GET", "POST"])
@shopkeeper_required
def shopkeeper_order_detail(order_id):
    """View order details and update status"""
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('shopkeeper_orders'))
    
    # Verify this order belongs to the shopkeeper's shop
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    
    if order['shop_id'] != shop['id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('shopkeeper_orders'))
    
    if request.method == "POST":
        # Case 1: Update Payment Status
        if request.form.get('verify_payment'):
            verified = request.form.get('payment_verified') == 'yes'
            Order.verify_payment(order_id, verified)
            flash('Payment update successfully', 'success')
            
        # Case 2: Update Order Status
        elif request.form.get('status'):
            status = request.form.get('status')
            notes = request.form.get('notes', '').strip()
            
            # Pass all info to update_status to handle in ONE connection
            delivery_info = {
                'name': request.form.get('delivery_boy_name', '').strip(),
                'phone': request.form.get('delivery_boy_phone', '').strip(),
                'location': request.form.get('current_location', '').strip()
            } if status == 'On The Way' else None
            
            Order.update_status(
                order_id, 
                status, 
                notes, 
                updated_by=f"Shopkeeper:{session['shopkeeper_username']}",
                delivery_info=delivery_info
            )
            flash('Delivery update successfully', 'success')
        
        return redirect(url_for('shopkeeper_order_detail', order_id=order_id))
    
    order_items = OrderItem.get_by_order(order_id)
    return render_template("shopkeeper_order_detail.html", order=order, order_items=order_items)


@app.route("/shopkeeper/notify-pickup/<int:order_id>", methods=["POST"])
@shopkeeper_required
def notify_pickup_ready(order_id):
    """Send SMS notification to customer for self-pickup orders"""
    order = Order.get_by_id(order_id)

    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    # Verify this order belongs to the shopkeeper's shop
    shopkeeper_id = session['shopkeeper_id']
    shop = Shop.get_by_shopkeeper(shopkeeper_id)

    if not shop or order['shop_id'] != shop['id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if order['delivery_type'] != 'pickup':
        return jsonify({'success': False, 'error': 'Not a pickup order'}), 400
    # Sanitize phone number — strip spaces, dashes, +91 prefix
    raw_phone = str(order['customer_phone']).strip()
    customer_phone = raw_phone.replace(" ", "").replace("-", "").replace("+91", "").replace("+", "")
    if len(customer_phone) != 10 or not customer_phone.isdigit():
        return jsonify({'success': False, 'error': f'Invalid phone number: {raw_phone}'}), 400

    message = "Sir Your order is ready pls take your order"

    # Send SMS notification
    sms_success = False
    sms_error = ""
    try:
        import requests as req
        response = req.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": FAST2SMS_API_KEY, "Content-Type": "application/x-www-form-urlencoded"},
            data={
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": customer_phone,
            },
            timeout=15
        )
        result = response.json()
        print(f"[PICKUP NOTIFY SMS] Order#{order_id} -> {customer_phone} | Response: {result}")
        if result.get('return') is True:
            sms_success = True
        else:
            error_msgs = result.get('message', [])
            sms_error = error_msgs[0] if isinstance(error_msgs, list) and error_msgs else str(error_msgs)
    except Exception as e:
        sms_error = str(e)

    # Send Email notification
    email_success = False
    email_error = ""
    customer_email = order['customer_email'] if 'customer_email' in order.keys() else None
    if customer_email:
        email_subject = f"Order Ready for Pickup - {order['order_number']}"
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #2c3e50;">Order Ready for Pickup!</h2>
                <p>Hello <strong>{order['customer_name']}</strong>,</p>
                <p>Great news! Your order from <strong>{shop['name']}</strong> is now ready for pickup.</p>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Order ID:</strong> {order['order_number']}</p>
                    <p style="margin: 0;"><strong>Shop Location:</strong> {shop['location']}</p>
                </div>
                <p>Please visit the shop to collect your delicious food.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #888;">This is an automated notification from FoodExpress. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        email_success, email_error = send_email(customer_email, email_subject, email_body)
    else:
        email_error = "Customer email not found"

    if sms_success or email_success:
        msg = "Notification sent successfully"
        if sms_success and email_success:
            msg += " (SMS & Email)"
        elif sms_success:
            msg += " (SMS only)"
        else:
            msg += " (Email only)"
        Order.set_notified(order_id)
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({
            'success': False, 
            'error': f"Failed to send notification. SMS: {sms_error} | Email: {email_error}"
        })


# ============================================
# ADMIN AUTHENTICATION ROUTES
# ============================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = Admin.get_by_username(username)
        if admin and Admin.verify_password(admin, password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session.permanent = True
            
            # Log login
            admin_email = admin['email'] if 'email' in admin.keys() else 'mdazhark735@gmail.com'
            log_user_login(admin['username'], admin_email, 'admin')
            
            flash('Login successful! Welcome back, Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.pop('_flashes', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))


# ============================================
# ADMIN DASHBOARD ROUTES
# ============================================

@app.route("/admin/dashboard", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    admin_id = session['admin_id']
    
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'update_profile':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not username:
                flash('Username cannot be empty!', 'error')
            elif password and password != confirm_password:
                flash('Passwords do not match!', 'error')
            else:
                update_data = {'username': username, 'email': email}
                if password:
                    update_data['password'] = password
                
                success = Admin.update(admin_id, **update_data)
                if success:
                    session['admin_username'] = username
                    flash('Admin profile updated successfully!', 'success')
                else:
                    flash('Username already exists!', 'error')
            return redirect(url_for('admin_dashboard'))

    admin = Admin.get_by_id(admin_id)
    stats = Statistics.get_counts()
    recent_orders = Order.get_all()[:10]
    shops = Shop.get_all(active_only=False)
    shopkeepers = Shopkeeper.get_all()
    
    return render_template(
        "admin_dashboard.html",
        admin=admin,
        stats=stats,
        recent_orders=recent_orders,
        shops=shops,
        shopkeepers=shopkeepers
    )


@app.route("/admin/shopkeepers", methods=["GET", "POST"])
@admin_required
def admin_shopkeepers():
    """Manage shopkeepers"""
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(request.url)
            
            shopkeeper_id = Shopkeeper.create(username, password, email, phone)
            if shopkeeper_id:
                # Create shop for this shopkeeper
                shop_name = request.form.get('shop_name', '').strip()
                shop_location = request.form.get('shop_location', '').strip()
                
                if shop_name:
                    Shop.create(
                        shopkeeper_id=shopkeeper_id,
                        name=shop_name,
                        location=shop_location,
                        phone=phone,
                        email=email
                    )
                
                flash('Shopkeeper added successfully!', 'success')
            else:
                flash('Username or email already exists', 'error')
            
        elif action == 'delete':
            shopkeeper_id = request.form.get('shopkeeper_id')
            Shopkeeper.delete(shopkeeper_id)
            flash('Shopkeeper deleted permanently', 'success')
    
    # Accurate Financial Aggregation Query (Delivered Missions Only)
    conn = get_db_connection()
    query = """
        SELECT sk.*, s.name as shop_name, s.id as shop_id,
               (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE shop_id = s.id AND order_status = 'Delivered' AND DATE(created_at) = DATE('now')) as daily_revenue,
               (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE shop_id = s.id AND order_status = 'Delivered' AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')) as monthly_revenue,
               (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE shop_id = s.id AND order_status = 'Delivered' AND strftime('%Y', created_at) = strftime('%Y', 'now')) as yearly_revenue,
               (SELECT COUNT(*) FROM orders WHERE shop_id = s.id AND order_status != 'User Cancelled') as order_count
        FROM shopkeepers sk
        LEFT JOIN shops s ON sk.id = s.shopkeeper_id
        WHERE sk.is_active = 1
        ORDER BY sk.created_at DESC
    """
    shopkeepers_rows = conn.execute(query).fetchall()
    
    # NEW: Fetch Month-by-Month History
    history_query = """
        SELECT shop_id, strftime('%Y-%m', created_at) as month_label, SUM(total_amount) as total
        FROM orders 
        WHERE order_status = 'Delivered'
        GROUP BY shop_id, month_label
        ORDER BY month_label DESC
    """
    history_rows = conn.execute(history_query).fetchall()
    
    # Map history to [shop_id]
    monthly_history = {}
    active_months = set()
    for row in history_rows:
        sid = row['shop_id']
        m_label = row['month_label']
        active_months.add(m_label)
        
        if sid not in monthly_history:
            monthly_history[sid] = []
        
        # Format month label for UI (e.g. 2026-04 -> APR 26)
        try:
            from datetime import datetime
            dt = datetime.strptime(m_label, '%Y-%m')
            short_name = dt.strftime('%b').upper()
        except:
            short_name = m_label
            
        monthly_history[sid].append({
            'month': m_label, 
            'short_name': short_name,
            'total': row['total']
        })
    
    # Sort active months for the "Calendar"
    sorted_months = sorted(list(active_months), reverse=True)
    calendar_months = []
    from datetime import datetime
    for m in sorted_months:
        dt = datetime.strptime(m, '%Y-%m')
        calendar_months.append({'label': m, 'name': dt.strftime('%b').upper()})

    conn.close()
    
    return render_template("admin_shopkeepers.html", 
                           shopkeepers=shopkeepers_rows, 
                           monthly_history=monthly_history,
                           calendar_months=calendar_months)


@app.route("/admin/monthly-report/<month>")
@admin_required
def admin_global_monthly_report(month):
    """View earnings for ALL shopkeepers for a specific month"""
    conn = get_db_connection()
    
    # Fetch all shopkeepers and their earnings for THIS month
    query = """
        SELECT sk.username, s.name as shop_name, s.id as shop_id,
               (SELECT COALESCE(SUM(total_amount), 0) 
                FROM orders 
                WHERE shop_id = s.id 
                AND order_status = 'Delivered' 
                AND strftime('%Y-%m', created_at) = ?) as monthly_total
        FROM shopkeepers sk
        LEFT JOIN shops s ON sk.id = s.shopkeeper_id
        WHERE sk.is_active = 1
    """
    report_data = conn.execute(query, (month,)).fetchall()
    
    # Platform Total
    platform_total = sum(row['monthly_total'] for row in report_data)
    
    from datetime import datetime
    try:
        dt = datetime.strptime(month, '%Y-%m')
        month_display = dt.strftime('%B %Y')
    except:
        month_display = month

    conn.close()
    return render_template("admin_global_monthly_report.html", 
                           report_data=report_data, 
                           month=month, 
                           month_display=month_display,
                           platform_total=platform_total)


@app.route("/admin/shopkeeper/<int:shopkeeper_id>/history/<month>")
@admin_required
def admin_shopkeeper_month_detail(shopkeeper_id, month):
    """View detailed orders for a specific shopkeeper and month"""
    conn = get_db_connection()
    shopkeeper = Shopkeeper.get_by_id(shopkeeper_id)
    if not shopkeeper:
        flash('Merchant node not found', 'error')
        return redirect(url_for('admin_shopkeepers'))
    
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    if not shop:
        flash('Associated shop not found', 'error')
        return redirect(url_for('admin_shopkeepers'))

    # Fetch all delivered orders for this shop and month
    query = """
        SELECT o.*, u.name as customer_name, u.phone as customer_phone, u.email as customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.shop_id = ? 
        AND o.order_status = 'Delivered' 
        AND strftime('%Y-%m', o.created_at) = ?
        ORDER BY o.created_at DESC
    """
    orders = conn.execute(query, (shop['id'], month)).fetchall()
    
    # Calculate total for the month
    total = sum(order['total_amount'] for order in orders)
    
    conn.close()
    
    return render_template("admin_shopkeeper_month_detail.html", 
                           shopkeeper=shopkeeper, 
                           shop=shop, 
                           month=month, 
                           orders=orders, 
                           total=total)


@app.route("/admin/shops", methods=["GET", "POST"])
@admin_required
def admin_shops():
    """Manage shops"""
    if request.method == "POST":
        action = request.form.get('action')
        shop_id = request.form.get('shop_id')
        print(f"DEBUG: Admin Shop Action={action}, ShopID={shop_id}")
        
        if action == 'toggle_status':
            conn = get_db_connection()
            shop = conn.execute("SELECT is_active FROM shops WHERE id = ?", (shop_id,)).fetchone()
            if shop:
                new_status = 0 if shop['is_active'] == 1 else 1
                conn.execute("UPDATE shops SET is_active = ? WHERE id = ?", (new_status, shop_id))
                conn.commit()
                status_text = "Activated" if new_status == 1 else "Deactivated"
                flash(f'Shop {status_text} successfully', 'success')
            conn.close()
        elif action == 'delete':
            Shop.delete(shop_id)
            flash('Shop permanently removed from active list', 'success')
        elif action == 'edit_shopkeeper':
            shopkeeper_id = request.form.get('shopkeeper_id')
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            update_data = {}
            if username: update_data['username'] = username
            if password: update_data['password'] = password
            
            if update_data and shopkeeper_id:
                try:
                    Shopkeeper.update(shopkeeper_id, **update_data)
                    flash('Shopkeeper credentials updated successfully!', 'success')
                except Exception as e:
                    flash('Error updating credentials (username might be taken)', 'error')
    
    shops = Shop.get_all(active_only=False)
    return render_template("admin_shops.html", shops=shops)


@app.route("/admin/orders")
@admin_required
def admin_orders():
    """View all orders"""
    orders = Order.get_all()
    shops = Shop.get_all(active_only=True)
    return render_template("admin_orders.html", orders=orders, shops=shops)


@app.route("/admin/orders/shop/<int:shop_id>")
@admin_required
def admin_shop_orders(shop_id):
    """View orders for a specific shop"""
    shop = Shop.get_by_id(shop_id)
    if not shop:
        flash('Shop not found', 'error')
        return redirect(url_for('admin_orders'))
    
    orders = Order.get_all_by_shop(shop_id)
    return render_template("admin_shop_orders.html", shop=shop, orders=orders)


@app.route("/admin/order/<int:order_id>")
@admin_required
def admin_view_order(order_id):
    """View detailed order intelligence and customer data"""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Mission data not found', 'error')
        return redirect(url_for('admin_orders'))
    
    conn = get_db_connection()
    order_items = conn.execute(
        """SELECT oi.id, oi.order_id, oi.food_item_id,
                  oi.item_name, oi.quantity, oi.price,
                  fi.image_path
           FROM order_items oi
           LEFT JOIN food_items fi ON oi.food_item_id = fi.id
           WHERE oi.order_id = ?""",
        (order_id,)
    ).fetchall()
    conn.close()
    return render_template("admin_view_order.html", order=order, items=order_items)


@app.route("/admin/users")
@admin_required
def admin_users():
    """View all users"""
    conn = get_db_connection()
    users = conn.execute(
        "SELECT * FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)


@app.route("/admin/user/<int:user_id>")
@admin_required
def admin_view_user(user_id):
    """View individual user details"""
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    orders = Order.get_by_user(user_id)
    return render_template("admin_view_user.html", user=user, orders=orders)


@app.route("/admin/shopkeeper/<int:shopkeeper_id>")
@admin_required
def admin_view_shopkeeper(shopkeeper_id):
    """View individual shopkeeper details"""
    shopkeeper = Shopkeeper.get_by_id(shopkeeper_id)
    if not shopkeeper:
        flash('Shopkeeper not found', 'error')
        return redirect(url_for('admin_shopkeepers'))
    
    shop = Shop.get_by_shopkeeper(shopkeeper_id)
    orders = Order.get_by_shop(shop['id']) if shop else []
    return render_template("admin_view_shopkeeper.html", shopkeeper=shopkeeper, shop=shop, orders=orders)


# ============================================
# CART & ORDER ROUTES
# ============================================

@app.route("/cart")
@login_required
def cart():
    """Shopping cart page"""
    return render_template("cart.html")


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    """Process checkout"""
    data = request.get_json()
    
    if not data or not data.get('items'):
        return jsonify({'error': 'No items in cart'}), 400
    
    # Store checkout data in session
    session['checkout_data'] = data
    
    return jsonify({'success': True, 'redirect': url_for('checkout_page')})


@app.route("/checkout/page")
@login_required
def checkout_page():
    """Checkout page"""
    checkout_data = session.get('checkout_data')
    if not checkout_data:
        flash('No items in cart', 'error')
        return redirect(url_for('cart'))
    
    # Sanitize image paths (fix Windows backslashes that corrupt URLs)
    if 'items' in checkout_data:
        for item in checkout_data['items']:
            if item.get('imagePath'):
                item['imagePath'] = item['imagePath'].replace('\\', '/')
    
    # Get shop info
    shop_id = checkout_data.get('shop_id')
    shop = Shop.get_by_id(shop_id) if shop_id else None
    
    return render_template("checkout.html", checkout_data=checkout_data, shop=shop)


@app.route("/payment/qr/<int:shop_id>")
@login_required
def payment_qr(shop_id):
    """Show payment QR code for a shop"""
    shop = Shop.get_by_id(shop_id)
    if not shop:
        flash('Shop not found', 'error')
        return redirect(url_for('home'))
    
    order_data = session.get('pending_order')
    if not order_data:
        flash('No pending order', 'error')
        return redirect(url_for('cart'))
    
    return render_template("payment_qr.html", shop=shop, order_data=order_data)


@app.route("/order/place", methods=["POST"])
@login_required
def place_order():
    """Place order"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = session['user_id']
    shop_id = data.get('shop_id')
    items = data.get('items', [])
    delivery_type = data.get('delivery_type')
    payment_type = data.get('payment_type')
    total_amount = data.get('total_amount')
    customer_name = data.get('customer_name')
    customer_phone = data.get('customer_phone')
    delivery_address = data.get('delivery_address', '')
    
    if not all([shop_id, items, delivery_type, payment_type, total_amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create order
    order_id, order_number = Order.create(
        user_id=user_id,
        shop_id=shop_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        delivery_type=delivery_type,
        payment_type=payment_type,
        total_amount=total_amount
    )
    
    # Add order items
    for item in items:
        OrderItem.create(
            order_id=order_id,
            food_item_id=item.get('id'),
            item_name=item.get('name'),
            quantity=item.get('quantity'),
            price=item.get('price')
        )
    
    # Store order info for payment/confirmation
    session['pending_order'] = {
        'order_id': order_id,
        'order_number': order_number,
        'shop_id': shop_id,
        'payment_type': payment_type,
        'total_amount': total_amount
    }
    
    # If online payment, redirect to QR page
    if payment_type == 'online':
        return jsonify({
            'success': True,
            'redirect': url_for('payment_qr', shop_id=shop_id)
        })
    
    # COD - go directly to success
    return jsonify({
        'success': True,
        'redirect': url_for('order_success', order_id=order_id)
    })


@app.route("/payment/upload", methods=["POST"])
@login_required
def upload_payment_screenshot():
    """Upload payment screenshot"""
    order_data = session.get('pending_order')
    if not order_data:
        return jsonify({'error': 'No pending order'}), 400
    
    if 'screenshot' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['screenshot']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        relative_path = upload_image_to_cloud_or_disk(file, 'payment_screenshots')
        Order.update_payment_screenshot(order_data['order_id'], relative_path)
        
        return jsonify({
            'success': True,
            'redirect': url_for('order_success', order_id=order_data['order_id'])
        })
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route("/order/success/<int:order_id>")
@login_required
def order_success(order_id):
    """Order success page"""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('home'))
    
    # Verify order belongs to current user
    if order['user_id'] != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))
    
    order_items = OrderItem.get_by_order(order_id)
    
    # Clear pending order
    session.pop('pending_order', None)
    session.pop('checkout_data', None)
    
    return render_template("order_success.html", order=order, order_items=order_items)


@app.route("/order/track/<order_number>")
def track_order(order_number):
    """Track order by order number"""
    order = Order.get_by_order_number(order_number)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('home'))
    
    order_items = OrderItem.get_by_order(order['id'])
    return render_template("order_status.html", order=order, order_items=order_items)


@app.route("/my-orders")
@login_required
def my_orders():
    """User's order history"""
    orders_raw = Order.get_by_user(session['user_id'])
    if not orders_raw:
        return render_template("my_orders.html", orders=[])
        
    orders = [dict(o) for o in orders_raw]
    order_ids = [o['id'] for o in orders]
    placeholders = ', '.join(['?'] * len(order_ids))
    
    conn = get_db_connection()
    items_raw = conn.execute(
        f"""SELECT oi.id as oi_id, oi.order_id, oi.food_item_id, 
                  oi.item_name, oi.quantity, oi.price,
                  fi.image_path, fi.category 
           FROM order_items oi 
           LEFT JOIN food_items fi ON oi.food_item_id = fi.id 
           WHERE oi.order_id IN ({placeholders})""",
        tuple(order_ids)
    ).fetchall()
    conn.close()
    
    items_by_order = {}
    for item in items_raw:
        item_dict = dict(item)
        oid = item_dict['order_id']
        if oid not in items_by_order:
            items_by_order[oid] = []
        items_by_order[oid].append(item_dict)
        
    for o in orders:
        o['order_items'] = items_by_order.get(o['id'], [])
        
    return render_template("my_orders.html", orders=orders)


# ============================================
# API ROUTES
# ============================================

@app.route("/get_cart_count")
def get_cart_count():
    """Get the current number of items in the cart"""
    # Simply count items in session's checkout_data if it exists
    # or return 0 if the user hasn't added anything yet
    checkout_data = session.get('checkout_data')
    if checkout_data and 'items' in checkout_data:
        count = sum(item.get('quantity', 0) for item in checkout_data['items'])
        return jsonify({'count': count})
    return jsonify({'count': 0})


@app.route("/api/shop/<int:shop_id>/menu")
def api_shop_menu(shop_id):
    """API: Get shop menu"""
    food_items = FoodItem.get_by_shop(shop_id, available_only=True)
    return jsonify([dict(item) for item in food_items])


@app.route("/api/order/<int:order_id>/status")
def api_order_status(order_id):
    """API: Get order status"""
    order = Order.get_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(dict(order))


@app.route("/api/order/<int:order_id>/status/history")
def api_order_status_history(order_id):
    """API: Get order status history"""
    conn = get_db_connection()
    history = conn.execute(
        """SELECT * FROM order_status_history 
           WHERE order_id = ? 
           ORDER BY created_at DESC""",
        (order_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(h) for h in history])


@app.route("/order/confirm-delivery/<int:order_id>", methods=["POST"])
@login_required
def confirm_delivery(order_id):
    """Customer confirms order delivery"""
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('profile'))
    
    # Verify order belongs to current user
    if order['user_id'] != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('profile'))
    
    # Confirm delivery
    Order.confirm_delivery(order_id)
    flash('Thank you! Your order delivery has been confirmed.', 'success')
    return redirect(url_for('profile'))


@app.route("/order/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    """Customer cancels their order"""
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('home'))
    
    # Verify order belongs to current user
    if int(order['user_id']) != int(session['user_id']):
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))
    
    # Update status to User Cancelled
    Order.update_status(order_id, 'User Cancelled', 'Cancelled by customer', updated_by='Customer')
    flash('Order is Successfully Cancel', 'success')
    return redirect(url_for('order_success', order_id=order_id))


# ============================================
# FILE SERVING (Secure)
# ============================================

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files securely"""
    # Fix for potential double 'uploads' in path
    if filename.startswith('uploads/'):
        filename = filename[8:]
    elif filename.startswith('static/uploads/'):
        filename = filename[15:]
        
    # On Vercel, check if the file exists in the /tmp/uploads folder.
    # If it doesn't exist there, fall back to serving it from the repository's static/uploads folder
    if os.environ.get('VERCEL'):
        tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(tmp_path):
            repo_static_uploads = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
            return send_from_directory(repo_static_uploads, filename)

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error_code=500, error_message="Internal server error"), 500


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    # Initialize database
    import schema_init
    
    print("Starting LPU Food Ordering System...")
    print("Admin Login: username='admin', password='admin123'")
    app.run(debug=True, host='0.0.0.0', port=5000)
