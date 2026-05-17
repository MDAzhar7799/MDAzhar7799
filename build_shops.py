import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

m_css = re.search(r'(/\* ===== NAVBAR ===== \*/.*?)(/\* ===== ANIMATIONS ===== \*/)', idx, re.DOTALL)
css_block = '''* { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --green-dark: #1f4037;
            --green-mid: #2d6a4f;
            --green-light: #99f2c8;
            --accent: #ff6b35;
            --bg: #f0f4f8;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: #1a1a2e;
            overflow-x: hidden;
        }

        ''' + m_css.group(1)

m_nav = re.search(r'(<!-- ===== NAVBAR ===== -->.*?</nav>)', idx, re.DOTALL)
# For shops page, we don't need 'features' link if we don't have it, but leaving it matches index exactly.

nav_block = m_nav.group(1)

m_footer = re.search(r'(<!-- ===== FOOTER ===== -->.*?</footer>)', idx, re.DOTALL)
footer_block = m_footer.group(1)

new_shops_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Shops - Azhar-foodExp</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
{css_block}
        
        /* Additional header specifically for shops list */
        .page-header {{
            background: linear-gradient(135deg, #0f1c17 0%, #1a3328 40%, #2d6a4f 100%);
            color: white;
            padding: 80px 24px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .page-header::after {{
            content: '';
            position: absolute; bottom: -80px; left: -80px;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(153,242,200,0.08) 0%, transparent 70%);
            border-radius: 50%;
        }}
        .page-header h1 {{
            font-size: clamp(2.4rem, 5vw, 3.8rem);
            font-weight: 800;
            margin-bottom: 22px;
            position: relative;
            z-index: 1;
        }}
        .page-header h1 i {{
            color: var(--green-light);
        }}
        .page-header p {{
            font-size: 1.1rem;
            color: rgba(255,255,255,0.75);
            max-width: 600px;
            margin: auto;
            position: relative;
            z-index: 1;
            line-height: 1.6;
        }}
        
        .shops-section {{
            padding: 80px 24px;
            background: var(--bg);
        }}
    </style>
</head>
<body>
{nav_block}

    <section class="page-header">
        <h1><i class="fas fa-store"></i> All Food Shops</h1>
        <p>Discover delicious food from various shops in LPU & LawGate. Skip the waiting lines and order straight to your location.</p>
    </section>

    <section class="shops-section">
        <div class="shops-grid" style="max-width: 1300px; margin: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(270px,1fr)); gap: 24px;">
            {{% if shops %}}
                {{% for shop in shops %}}
                <div class="shop-card">
                    <div class="shop-img">
                        {{% if shop.logo_path %}}
                            <img src="/{{{{ shop.logo_path if shop.logo_path.startswith('uploads') else 'uploads/' + shop.logo_path }}}}" alt="{{{{ shop.name }}}}">
                        {{% else %}}
                            <img src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&q=80" alt="{{{{ shop.name }}}}">
                        {{% endif %}}
                        <div class="shop-overlay"></div>
                    </div>
                    <div class="shop-body">
                        <h3>{{{{ shop.name }}}}</h3>
                        <div class="shop-loc">
                            <i class="fas fa-map-marker-alt" style="color:var(--green-mid)"></i>
                            {{{{ shop.location or 'LPU Campus' }}}}
                        </div>
                        <p style="color: #666; font-size: 0.88rem; margin-bottom: 15px; min-height: 40px; line-height: 1.5;">
                            {{{{ shop.description or 'Delicious food available for order. Click to view menu.' }}}}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; font-size: 0.85rem; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.05);">
                            {{% if shop.delivery_available %}}
                                <span style="color: #2e7d32; font-weight: 700; display:flex; align-items:center; gap:6px;"><i class="fas fa-motorcycle"></i> Delivery: ₹{{{{ shop.delivery_charge or 20 }}}}</span>
                            {{% else %}}
                                <span style="color: var(--accent); font-weight: 700; display:flex; align-items:center; gap:6px;"><i class="fas fa-walking"></i> Pickup Only</span>
                            {{% endif %}}
                        </div>
                        <a href="{{{{ url_for('shop_menu', shop_id=shop.id) }}}}" class="btn-view" style="width: 100%;">
                            <i class="fas fa-utensils"></i> View Menu
                        </a>
                    </div>
                </div>
                {{% endfor %}}
            {{% else %}}
                <div class="no-shops" style="grid-column: 1/-1; text-align: center; padding: 80px 20px; color: #bbb;">
                    <i class="fas fa-store-slash" style="font-size: 4rem; display: block; margin-bottom: 16px;"></i>
                    <h3 style="color: #888;">No shops available yet</h3>
                    <p style="color:#bbb;margin-top:8px">Check back soon — more shops are coming!</p>
                </div>
            {{% endif %}}
        </div>
    </section>

{footer_block}
</body>
</html>'''

with open('templates/shops.html', 'w', encoding='utf-8') as f:
    f.write(new_shops_html)
print("shops.html rewritten successfully!")
