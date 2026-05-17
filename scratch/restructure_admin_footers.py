import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

# New footer HTML structure
new_footer_html = """        <div class="footer-grid">
            <div class="footer-col">
                <div class="footer-brand">
                    <i class="fas fa-utensils"></i>
                    <h2>FoodExpress</h2>
                </div>
                <p class="footer-desc">
                    Order smart, skip queues, eat better. Built for LPU & LawGate students, staff and everyone on campus who values their time.
                </p>
                <div class="contact-item" style="margin-top: 20px;">
                    <i class="fas fa-envelope"></i>
                    <p class="contact-text">mdazhark735@gmail.com</p>
                </div>
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
                <h4>System Portals</h4>
                <ul class="footer-links">
                    <li><a href="/shopkeeper/login"><i class="fas fa-chevron-right"></i> Shopkeeper Portal</a></li>
                    <li><a href="/admin/dashboard"><i class="fas fa-chevron-right"></i> Admin Dashboard</a></li>
                </ul>
            </div>
        </div>
        <div class="copyright">
            © 2026 FoodExpress — Made by MD Azhar | Built for everyone, loved by students
        </div>"""

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.startswith('admin_') and file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Update Grid CSS to 3 columns
            content = re.sub(r'grid-template-columns: 2fr 1fr 1fr 1fr;', 'grid-template-columns: 1.5fr 1fr 1fr;', content)
            
            # 2. Replace the entire footer grid + copyright
            footer_pattern = r'<div class="footer-grid">.*?</div>\s*<div class="copyright">.*?</div>'
            new_content = re.sub(footer_pattern, new_footer_html, content, flags=re.DOTALL)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Restructured Footer: {file}")
