import os

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_view_order.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '<h1>MISSION <span>': '<h1>ORDER <span>',
    "'LOG-FAIL'": "'N/A'",
    'Customer Intel': 'Customer Details',
    'Contact Link (Phone)': 'Phone Number',
    'Digital Identity (Email)': 'Email Address',
    'Delivery Coordinates (Address)': 'Delivery Address',
    'Order Payload': 'Order Items',
    'Resource Name': 'Item Name',
    'Gross Payload Value': 'Total Amount',
    'Node Details': 'Order Info',
    'Source Shop': 'Shop Name',
    'Logistics Type': 'Delivery Type',
    'Timestamp': 'Date & Time',
    'Fiscal Proof': 'Payment Proof'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Simplified wording in admin_view_order.html")
