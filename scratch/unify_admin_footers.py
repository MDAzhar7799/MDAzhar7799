import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

# Uniform 4-column footer
uniform_footer_html = """    <footer class="footer-main">
        <div class="footer-grid">
            <div class="footer-col">
                <div class="footer-brand">
                    <i class="fas fa-utensils"></i>
                    <h2>FoodExpress</h2>
                </div>
                <p class="footer-desc">
                    Order smart, skip queues, eat better. Built for LPU & LawGate students, staff and everyone on campus who values their time.
                </p>
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
            <div class="footer-col">
                <h4>Contact</h4>
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    <p class="contact-text">mdazhark735@gmail.com</p>
                </div>
            </div>
        </div>
        <div class="copyright">
            © 2026 FoodExpress — Made by MD Azhar | Built for everyone, loved by students
        </div>
    </footer>"""

# Footer styles to ensure consistency
footer_styles = """
        /* ===== FOOTER STYLES ===== */
        .footer-main {
            background: #020617;
            padding: 80px 40px 40px;
            color: #94a3b8;
            margin-top: 100px;
            border-top: 1px solid rgba(255,255,255,0.05);
            text-align: left;
        }
        .footer-grid {
            max-width: 1300px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 60px;
            margin-bottom: 60px;
        }
        .footer-col h4 { color: white; font-weight: 800; margin-bottom: 25px; font-size: 1.1rem; }
        .footer-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
        .footer-brand i { 
            background: #22c55e; 
            color: white; 
            width: 50px; 
            height: 50px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border-radius: 14px; 
            font-size: 1.6rem; 
        }
        .footer-brand h2 { 
            color: white; 
            font-size: 2rem; 
            font-weight: 900; 
            letter-spacing: -1.5px;
            margin: 0;
        }
        .footer-desc { line-height: 1.6; font-size: 0.95rem; font-weight: 500; }
        .footer-links { list-style: none; padding: 0; }
        .footer-links li { margin-bottom: 15px; }
        .footer-links a { color: #94a3b8; text-decoration: none; font-weight: 500; transition: 0.3s; display: flex; align-items: center; gap: 10px; }
        .footer-links a:hover { color: #22c55e; padding-left: 5px; }
        .footer-links i { font-size: 0.7rem; }
        .contact-item { display: flex; gap: 15px; margin-bottom: 20px; align-items: center; }
        .contact-item i { color: #22c55e; font-size: 1.1rem; }
        .contact-text { font-size: 0.9rem; font-weight: 500; line-height: 1.4; margin: 0; }
        .copyright { text-align: center; padding-top: 30px; border-top: 1px solid rgba(255,255,255,0.05); font-weight: 700; font-size: 0.95rem; color: #ffffff; }
"""

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.startswith('admin_') and file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Ensure the styles are present in the <style> block
            if '/* ===== FOOTER STYLES ===== */' not in content:
                style_end_pattern = r'</style>'
                if re.search(style_end_pattern, content):
                    content = re.sub(style_end_pattern, footer_styles + '\n    </style>', content, count=1)
            else:
                # Update existing styles
                style_pattern = r'/\* ===== FOOTER STYLES ===== \*/.*?copyright {.*?}'
                content = re.sub(style_pattern, footer_styles, content, flags=re.DOTALL)

            # 2. Replace the <footer> block entirely
            footer_pattern = r'<footer.*?>.*?</footer>'
            new_content = re.sub(footer_pattern, uniform_footer_html, content, flags=re.DOTALL)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Unified Footer: {file}")
