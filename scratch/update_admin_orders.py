import os
import re

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_orders.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Text Replacements
replacements = {
    'Mission Archive': 'Order History',
    'Day-by-Day logistical history of the Azhar-foodExp grid.': 'Day-by-Day history of all orders.',
    "Today's Payload Volume": "Today's Orders",
    ' Missions Active': ' Orders Today',
    'Archive Status': 'System Status',
    'Mission ID': 'Order ID',
    'Operative Detail (Email/Phone)': 'Customer Details',
    '<th>Node</th>': '<th>Shop Name</th>',
    '<th>Logistics</th>': '<th>Delivery Type</th>',
    '<th>Value</th>': '<th>Total Amount</th>',
    '<th>Intelligence</th>': '<th>Action</th>',
    'VIEW INTEL': 'VIEW DETAILS',
    'No missions found in the archive.': 'No orders found.'
}
for old, new in replacements.items():
    content = content.replace(old, new)

# 2. CSS Replacements for text sizing
content = content.replace(
    'th { padding: 20px 25px; font-size: 0.75rem; font-weight: 800; color: var(--text-muted); border-bottom: 2px solid #f3f4f6; text-transform: uppercase; letter-spacing: 1px; }',
    'th { padding: 20px 25px; font-size: 0.95rem; font-weight: 900; color: var(--text-dark); border-bottom: 2px solid #f3f4f6; text-transform: uppercase; letter-spacing: 0.5px; }'
)
content = content.replace(
    'td { padding: 20px 25px; font-size: 0.9rem; border-bottom: 1px solid #f3f4f6; font-weight: 500; }',
    'td { padding: 20px 25px; font-size: 0.95rem; border-bottom: 1px solid #f3f4f6; font-weight: 700; }'
)

# 3. Add Filter CSS
filter_css = """        /* ===== FILTER STYLES ===== */
        .filter-controls { display: flex; gap: 15px; align-items: center; margin-bottom: 25px; }
        .filter-btn {
            background: white; border: 2px solid #e5e7eb; padding: 10px 24px;
            border-radius: 12px; font-weight: 800; color: var(--text-muted);
            cursor: pointer; transition: 0.3s; font-family: 'Outfit'; font-size: 0.9rem;
        }
        .filter-btn:hover { border-color: var(--blue); color: var(--blue); }
        .filter-btn.active { background: var(--blue); border-color: var(--blue); color: white; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); }
        .filter-date {
            padding: 9px 15px; border-radius: 12px; border: 2px solid #e5e7eb;
            font-family: 'Outfit'; font-weight: 700; color: var(--text-dark);
            outline: none; transition: 0.3s; cursor: pointer; font-size: 0.9rem;
        }
        .filter-date:focus { border-color: var(--blue); }
    </style>"""
if '/* ===== FILTER STYLES ===== */' not in content:
    content = content.replace('    </style>', filter_css)


# 4. Inject Filter HTML Buttons before .card
filter_html = """        <div class="filter-controls">
            <button onclick="filterOrders('all')" class="filter-btn active" id="btn-all"><i class="fas fa-list"></i> All Orders</button>
            <button onclick="filterOrders('today')" class="filter-btn" id="btn-today"><i class="fas fa-bolt"></i> Today</button>
            <input type="date" id="datePicker" class="filter-date" onchange="filterOrders('date', this.value)">
        </div>
        <div class="card">"""
content = content.replace('<div class="card">', filter_html, 1)

# 5. Add data-date to rows
# Replace <tr> enclosing date-separator
# Wait, we need to be careful with regex here.
# The table body looks like:
# <tbody> ...
#   <tr>
#       <td colspan="7">
#           <div class="date-separator">

content = re.sub(
    r'(<tr>\s*<td colspan="7">\s*<div class="date-separator">)',
    r'<tr class="date-sep-row" data-date="{{ order_date }}">\n                                <td colspan="7">\n                                    <div class="date-separator">',
    content
)

# Replace the order rows
# <tr>
#   <td class="mission-id">
content = re.sub(
    r'(<tr>\s*<td class="mission-id">)',
    r'<tr class="order-row" data-date="{{ order_date }}">\n                            <td class="mission-id">',
    content
)

# 6. Inject Javascript at bottom
js_code = """
<script>
    const todayDate = "{{ today_data.latest_date }}";
    
    function filterOrders(type, selectedDate = null) {
        // Reset buttons
        document.getElementById('btn-all').classList.remove('active');
        document.getElementById('btn-today').classList.remove('active');
        
        let targetDate = "";
        
        if (type === 'all') {
            document.getElementById('btn-all').classList.add('active');
            document.getElementById('datePicker').value = "";
        } else if (type === 'today') {
            document.getElementById('btn-today').classList.add('active');
            targetDate = todayDate;
            document.getElementById('datePicker').value = targetDate;
        } else if (type === 'date') {
            targetDate = selectedDate;
            if(targetDate === todayDate) {
                document.getElementById('btn-today').classList.add('active');
            }
        }
        
        // Filter rows
        const rows = document.querySelectorAll('tbody tr[data-date]');
        let visibleCount = 0;
        
        rows.forEach(row => {
            if (type === 'all') {
                row.style.display = '';
                visibleCount++;
            } else {
                if (row.getAttribute('data-date') === targetDate) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            }
        });
        
        // Handle empty state
        const emptyMsg = document.getElementById('empty-msg-row');
        if (visibleCount === 0) {
            if (!emptyMsg) {
                const tbody = document.querySelector('tbody');
                const tr = document.createElement('tr');
                tr.id = 'empty-msg-row';
                tr.innerHTML = '<td colspan="7" style="text-align: center; padding: 50px; font-weight: 700; color: var(--text-muted);">No orders found for selected filter.</td>';
                tbody.appendChild(tr);
            } else {
                emptyMsg.style.display = '';
            }
        } else if (emptyMsg) {
            emptyMsg.style.display = 'none';
        }
    }
</script>
</body>"""

if "function filterOrders" not in content:
    content = content.replace('</body>', js_code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated admin_orders.html")
