import os
import re

# 1. Update admin_orders.html to remove "No reason provided"
path_orders = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_orders.html'
with open(path_orders, 'r', encoding='utf-8') as f:
    content_orders = f.read()

content_orders = content_orders.replace(
    '{% else %}\n                                            <span style="font-size: 0.75rem; font-weight: 600; text-transform: none; margin-top: 3px; letter-spacing: 0; color: #ef4444;">No reason provided</span>\n                                        {% endif %}',
    '{% endif %}'
)

with open(path_orders, 'w', encoding='utf-8') as f:
    f.write(content_orders)

# 2. Update admin_view_order.html to show "Shopkeeper Cancelled" in red
path_view = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_view_order.html'
with open(path_view, 'r', encoding='utf-8') as f:
    content_view = f.read()

# Current HTML line: <span class="status-badge status-{{ (order.order_status or 'pending')|lower|replace(' ', '-') }}">{{ order.order_status or 'Pending' }}</span>
# Wait, I might have lowered it without replace in admin_view_order.html previously? Let's be safe.
old_badge_regex = r'<span class="status-badge status-\{\{.*?\}\}.*?\{\{.*?\}\}</span>'

new_badge = """{% if order.order_status == 'Cancelled' %}
                        <span class="status-badge" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; font-weight: 900;">SHOPKEEPER CANCELLED</span>
                    {% else %}
                        <span class="status-badge status-{{ (order.order_status or 'pending')|lower|replace(' ', '-') }}">{{ order.order_status or 'Pending' }}</span>
                    {% endif %}"""

content_view = re.sub(old_badge_regex, new_badge, content_view)

# Add CSS for .status-badge.status-user-cancelled and .status-badge.status-cancelled if missing
css_additions = """        .status-user-cancelled { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
        .status-cancelled { background: #fff7ed; color: #ea580c; border: 1px solid #ffedd5; }"""

if '.status-user-cancelled' not in content_view:
    content_view = content_view.replace('.status-delivered { background: #f1f5f9; color: #475569; }', 
                                        '.status-delivered { background: #f1f5f9; color: #475569; }\n' + css_additions)


with open(path_view, 'w', encoding='utf-8') as f:
    f.write(content_view)

print("Updates completed.")
