import os
import re

directory = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

replacements = {
    r'Entity Protocol \(Shops\)': 'Shop Management',
    r'Monitor and manage all culinary nodes within the FoodExpress grid.': 'Manage and monitor all active shops on the FoodExpress platform.',
    r'Node Name': 'Shop Name',
    r'Controller': 'Owner',
    r'Deployment': 'Date Created',
    r'Logic': 'Shops',
    r'Shutdown this entity node\?': 'Are you sure you want to delete this shop?',
    r'Merchant ID \(Username\)': 'Username',
    r'Security Code \(Password\)': 'Password',
    r'Primary Email': 'Email',
    r'Entity Name \(Shop\)': 'Shop Name',
    r'Grid Deployment \(Location\)': 'Location',
    r'Comms Reference \(Phone\)': 'Phone Number',
    r'INITIALIZE & LINK SHOPKEEPER': 'Add Shopkeeper',
    r'GLOBAL MONTHLY TRACKER': 'Monthly Reports',
    r'INTELLIGENCE TABLE': 'Shopkeepers',
    r'Mission Intelligence': 'Order Data',
    r'Mission #': 'Order ID',
    r'Operative': 'Customer',
    r'Target': 'Delivery',
    r'Status Phase': 'Status',
    r'SYSTEM SUMMARY': 'Dashboard Overview',
    r'TOTAL REVENUE': 'Total Revenue',
    r'ACTIVE SHOPS': 'Active Shops',
    r'TOTAL USERS': 'Total Users',
    r'TOTAL MISSIONS': 'Total Orders',
    r'GLOBAL ANALYTICS CALENDAR': 'Monthly Reports',
    r'Shopkeeper Detail': 'Shopkeeper Info',
    r'Summary': 'Dashboard',
    r'Merchants': 'Shopkeepers'
}

for filename in os.listdir(directory):
    if filename.startswith('admin_') and filename.endswith('.html'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")
