import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'
mini_files = ['admin_users.html', 'admin_view_user.html', 'admin_view_order.html', 'admin_view_shopkeeper.html', 'admin_login.html']

for file in mini_files:
    path = os.path.join(templates_dir, file)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip any remaining added footer styles entirely by replacing everything from /* ===== FOOTER STYLES ===== */ to </style>
    content = re.sub(r'\s*/\* ===== FOOTER STYLES ===== \*/.*?</style>', '\n    </style>', content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cleaned CSS in: {file}")
