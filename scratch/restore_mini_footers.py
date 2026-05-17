import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

# Files to restore to "mini" footer
mini_files = ['admin_users.html', 'admin_view_user.html', 'admin_view_order.html', 'admin_view_shopkeeper.html']

for file in mini_files:
    path = os.path.join(templates_dir, file)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the injected CSS
    content = re.sub(r'\s*/\* ===== FOOTER STYLES ===== \*/.*?\.copyright \{.*?\n\s*\}', '', content, flags=re.DOTALL)
    
    # Replace the injected large footer HTML with the mini footer
    mini_footer = '    <footer>\n        <p>© 2026 FoodExpress. System Administration. Power by AZHAR™</p>\n    </footer>'
    content = re.sub(r'<footer class="footer-main">.*?</footer>', mini_footer, content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Restored mini footer: {file}")

# Fix admin_login.html
login_path = os.path.join(templates_dir, 'admin_login.html')
if os.path.exists(login_path):
    with open(login_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove injected CSS
    content = re.sub(r'\s*/\* ===== FOOTER STYLES ===== \*/.*?\.copyright \{.*?\n\s*\}', '', content, flags=re.DOTALL)
    
    # Original 3-column login footer html
    login_footer = """    <footer>
        <div class="footer-grid">
            <div class="footer-brand-col">
                <div class="flabel">
                    <div class="flogo"><i class="fas fa-utensils"></i></div>
                    <h2>FoodExpress</h2>
                </div>
                <p>Order smart, skip queues, eat better. Built for LPU & LawGate students, staff and everyone on campus who values their time.</p>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul class="footer-links">
                    <li><a href="/"><i class="fas fa-chevron-right"></i> Home</a></li>
                    <li><a href="/shops"><i class="fas fa-chevron-right"></i> All Shops</a></li>
                    <li><a href="#founder"><i class="fas fa-chevron-right"></i> Founder</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>For Shops</h4>
                <ul class="footer-links">
                    <li><a href="/shopkeeper/login"><i class="fas fa-chevron-right"></i> Shopkeeper Login</a></li>
                    <li><a href="/admin/dashboard"><i class="fas fa-chevron-right"></i> Admin Panel</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            © 2026 FoodExpress — Made by MD Azhar | Built for everyone, loved by students
        </div>
    </footer>"""
    
    content = re.sub(r'<footer class="footer-main">.*?</footer>', login_footer, content, flags=re.DOTALL)
    
    with open(login_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Restored original login footer: admin_login.html")
