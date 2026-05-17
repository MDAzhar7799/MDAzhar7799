import os
import re

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_orders.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the count logic to exclude User Cancelled
old_count_logic = """            {% for o in orders %}
                {% if (o.created_at or "")[:10] == today_data.latest_date %}
                    {% set today_data.today_count = today_data.today_count + 1 %}
                {% endif %}
            {% endfor %}"""

new_count_logic = """            {% for o in orders %}
                {% if (o.created_at or "")[:10] == today_data.latest_date and o.order_status != 'User Cancelled' %}
                    {% set today_data.today_count = today_data.today_count + 1 %}
                {% endif %}
            {% endfor %}"""
content = content.replace(old_count_logic, new_count_logic)

# 2. Update the table loop to wrap everything in if condition
old_table_loop = """                    {% set tracker = namespace(current_date="") %}
                    {% for order in orders %}
                        {% set order_date = (order.created_at or "")[:10] %}"""

new_table_loop = """                    {% set tracker = namespace(current_date="") %}
                    {% for order in orders %}
                        {% if order.order_status != 'User Cancelled' %}
                            {% set order_date = (order.created_at or "")[:10] %}"""
content = content.replace(old_table_loop, new_table_loop)

# 3. Add endif before the endfor
old_end_loop = """                            <td>
                                <a href="{{ url_for('admin_view_order', order_id=order.id) }}" class="view-link">VIEW DETAILS</a>
                            </td>
                        </tr>
                    {% endfor %}"""
new_end_loop = """                            <td>
                                <a href="{{ url_for('admin_view_order', order_id=order.id) }}" class="view-link">VIEW DETAILS</a>
                            </td>
                        </tr>
                        {% endif %}
                    {% endfor %}"""
content = content.replace(old_end_loop, new_end_loop)

# 4. Replace the status pill display
old_status = """                            <td>
                                <span class="status-pill status-{{ (order.order_status or 'pending')|lower|replace(' ', '-') }}">
                                    {{ order.order_status or 'Pending' }}
                                </span>
                            </td>"""

new_status = """                            <td>
                                {% if order.order_status == 'Cancelled' %}
                                    <span class="status-pill" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; display: inline-flex; flex-direction: column; text-align: left; line-height: 1.4; padding: 8px 14px;">
                                        <span style="font-weight: 900;">SHOPKEEPER CANCELLED</span>
                                        {% if order.cancellation_reason %}
                                            <span style="font-size: 0.75rem; font-weight: 600; text-transform: none; margin-top: 3px; letter-spacing: 0;">Reason: {{ order.cancellation_reason }}</span>
                                        {% else %}
                                            <span style="font-size: 0.75rem; font-weight: 600; text-transform: none; margin-top: 3px; letter-spacing: 0; color: #ef4444;">No reason provided</span>
                                        {% endif %}
                                    </span>
                                {% else %}
                                    <span class="status-pill status-{{ (order.order_status or 'pending')|lower|replace(' ', '-') }}">
                                        {{ order.order_status or 'Pending' }}
                                    </span>
                                {% endif %}
                            </td>"""
content = content.replace(old_status, new_status)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied User Cancelled hidden logic and Shopkeeper Cancelled red text with reason.")
