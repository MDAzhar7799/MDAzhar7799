import os
import re

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_dashboard.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The CSS block to replace
new_css = """        /* ===== FOOTER ===== */
        footer {
            background: linear-gradient(135deg, #020617, #0f172a);
            padding: 80px 30px 0;
            color: rgba(255,255,255,0.4); font-family: 'Outfit', sans-serif;
            text-align: left;
        }
        .footer-grid {
            max-width: 1300px; margin: auto;
            display: grid; grid-template-columns: 2fr 1fr 1fr;
            gap: 60px; padding-bottom: 60px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .footer-brand-col .flabel {
            display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
        }
        .footer-brand-col .flogo {
            width: 42px; height: 42px; border-radius: 12px;
            background: linear-gradient(135deg, #22c55e, #16a34a);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.1rem; color: white;
        }
        .footer-brand-col h2 { font-size: 1.4rem; font-weight: 900; color: white; margin: 0; }
        .footer-brand-col p { color: rgba(255,255,255,0.4); font-size: 0.95rem; line-height: 1.75; max-width: 380px; margin: 0; }
        .footer-col h4 { font-size: 1rem; font-weight: 800; color: white; margin-bottom: 22px; }
        .footer-links { list-style: none; padding: 0; margin: 0; }
        .footer-links li { margin-bottom: 12px; }
        .footer-links a {
            color: rgba(255,255,255,0.4); text-decoration: none;
            font-size: 0.9rem; font-weight: 500; transition: 0.3s;
            display: flex; align-items: center; gap: 7px;
        }
        .footer-links a:hover { color: #4ade80; padding-left: 4px; }
        .footer-links a i { font-size: 0.75rem; color: #22c55e; }
        .footer-bottom {
            max-width: 1300px; margin: auto; padding: 30px 0;
            text-align: center; color: #ffffff;
            font-size: 0.9rem; font-weight: 700;
        }"""

# Replace the old CSS
content = re.sub(r'\s*/\* ===== FOOTER STYLES ===== \*/.*?\.copyright \{.*?\n\s*\}', '\n' + new_css, content, flags=re.DOTALL)

# The HTML block to replace
new_html = """    <footer>
        <div class="footer-grid">
            <!-- Brand -->
            <div class="footer-brand-col">
                <div class="flabel">
                    <div class="flogo"><i class="fas fa-utensils"></i></div>
                    <h2>FoodExpress</h2>
                </div>
                <p>A premium food ordering experience for students and faculty across LPU & LawGate. Fresh food, fast delivery, every time.</p>
            </div>
            <!-- Quick Links -->
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul class="footer-links">
                    <li><a href="{{ url_for('home') }}"><i class="fas fa-chevron-right"></i> Home</a></li>
                    <li><a href="{{ url_for('shops_list') }}"><i class="fas fa-chevron-right"></i> All Shops</a></li>
                    <li><a href="#founder"><i class="fas fa-chevron-right"></i> Founder</a></li>
                </ul>
            </div>
            <!-- Support -->
            <div class="footer-col">
                <h4>Support</h4>
                <ul class="footer-links">
                    <li><a href="{{ url_for('my_orders') }}"><i class="fas fa-chevron-right"></i> Track Order</a></li>
                    <li><a href="{{ url_for('login') }}"><i class="fas fa-chevron-right"></i> Login</a></li>
                    <li><a href="{{ url_for('register') }}"><i class="fas fa-chevron-right"></i> Register</a></li>
                    <li><a href="mailto:mdazhark735@gmail.com"><i class="fas fa-envelope"></i> mdazhark735@gmail.com</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 FoodExpress — Made by MD Azhar | Built for everyone, loved by students</p>
        </div>
    </footer>"""

# Replace the old HTML
content = re.sub(r'<footer class="footer-main">.*?</footer>', new_html, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated admin_dashboard.html")
