import os

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_users.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_css = """
        /* ===== CONTAINER ===== */
        .container { max-width: 1300px; margin: 40px auto; padding: 0 20px; }
 
        .page-header h1 { font-size: 1.8rem; font-weight: 800; margin-bottom: 5px; }
        .page-header p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 30px; }
 
        .card { background: white; border-radius: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); overflow: hidden; }
 
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { padding: 20px 25px; font-size: 0.75rem; font-weight: 800; color: var(--text-muted); border-bottom: 2px solid #f3f4f6; text-transform: uppercase; letter-spacing: 1px; }
        td { padding: 20px 25px; font-size: 0.95rem; border-bottom: 1px solid #f3f4f6; font-weight: 500; }
 
        .user-id { font-weight: 850; color: var(--blue); font-size: 0.85rem; }
        .action-link { color: var(--blue); text-decoration: none; font-weight: 800; font-size: 0.85rem; }
 
        footer { background: #020617; padding: 60px 20px; color: #94a3b8; text-align: center; margin-top: 100px; }
    </style>"""

content = content.replace('    </style>', missing_css)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed admin_users.html")
