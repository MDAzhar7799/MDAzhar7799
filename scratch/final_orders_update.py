import os
import re

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_orders.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS for customer details, delivery type, and status pills
css_replace = """        .customer-cel { line-height: 1.4; }
        .customer-name { font-weight: 850; display: block; font-size: 1.05rem; }
        .customer-email { font-size: 0.95rem; color: var(--text-dark); display: block; font-weight: 700; }
        .customer-phone { font-size: 0.9rem; color: var(--text-muted); display: block; font-weight: 700; margin-top: 3px; }
        .delivery-type { font-size: 0.95rem; font-weight: 800; text-transform: capitalize; }
 
        .status-pill { padding: 6px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }
        .status-pill.status-placed { background: #eff6ff; color: #1e40af; }
        .status-pill.status-delivered { background: #f1f5f9; color: #475569; }
        .status-pill.status-preparing { background: #fffbeb; color: #92400e; }
        .status-pill.status-ready { background: #ecfdf5; color: #065f46; }
        .status-pill.status-user-cancelled { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
        .status-pill.status-cancelled { background: #fff7ed; color: #ea580c; border: 1px solid #ffedd5; }"""

old_css = r'\.customer-cel \{ line-height: 1\.4; \}.*?\.status-pill\.status-ready \{ background: #ecfdf5; color: #065f46; \}'
content = re.sub(old_css, css_replace, content, flags=re.DOTALL)

# 2. Update Filter CSS
new_filter_css = """        /* ===== FILTER STYLES ===== */
        .filter-controls { 
            background: #0f172a; border: 2px solid #ea580c; padding: 15px 25px;
            border-radius: 16px; display: flex; gap: 15px; align-items: center; 
            margin-bottom: 25px; box-shadow: 0 10px 25px rgba(234, 88, 12, 0.1);
        }
        .filter-btn {
            background: transparent; border: none; padding: 10px 24px;
            border-radius: 12px; font-weight: 800; color: rgba(255,255,255,0.7);
            cursor: pointer; transition: 0.3s; font-family: 'Outfit'; font-size: 0.95rem;
            display: flex; align-items: center; gap: 8px;
        }
        .filter-btn:hover { color: white; background: rgba(255,255,255,0.05); }
        .filter-btn.active { background: #ea580c; color: white; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.4); }
        .filter-label { color: white; font-weight: 800; font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase; margin-left: auto; }
        .filter-date {
            padding: 10px 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05); font-family: 'Outfit'; font-weight: 800; color: white;
            outline: none; transition: 0.3s; cursor: pointer; font-size: 0.95rem;
        }
        .filter-date:focus { border-color: #ea580c; background: rgba(255,255,255,0.1); }
        .filter-date::-webkit-calendar-picker-indicator { filter: invert(1) sepia(1) saturate(5) hue-rotate(350deg); opacity: 0.8; cursor: pointer; }
    </style>"""

old_filter_css = r'/\* ===== FILTER STYLES ===== \*/.*?</style>'
content = re.sub(old_filter_css, new_filter_css, content, flags=re.DOTALL)

# 3. Update Filter HTML
new_filter_html = """        <div class="filter-controls">
            <button onclick="filterOrders('all')" class="filter-btn active" id="btn-all"><i class="fas fa-layer-group"></i> All Orders</button>
            <button onclick="filterOrders('today')" class="filter-btn" id="btn-today"><i class="fas fa-calendar-check"></i> Today</button>
            <span class="filter-label">SPECIFIC DATE:</span>
            <input type="date" id="datePicker" class="filter-date" onchange="filterOrders('date', this.value)">
        </div>"""
old_filter_html = r'<div class="filter-controls">.*?</div>\s*<div class="card">'
content = re.sub(old_filter_html, new_filter_html + '\n        <div class="card">', content, flags=re.DOTALL)

# 4. Update HTML table rows for email, phone, delivery type, and status pill class
content = content.replace('<span style="font-size: 0.75rem; color: var(--text-muted);">{{ order.customer_phone }}</span>', '<span class="customer-phone">{{ order.customer_phone }}</span>')
content = content.replace('<td style="font-size: 0.8rem;">{{ order.delivery_type }}</td>', '<td class="delivery-type">{{ order.delivery_type }}</td>')
content = content.replace('<span class="status-pill status-{{ (order.order_status or \'pending\')|lower }}">', '<span class="status-pill status-{{ (order.order_status or \'pending\')|lower|replace(\' \', \'-\') }}">')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated admin_orders.html completely")
