import os

path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates\admin_view_order.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_css = """
        /* ===== CONTAINER ===== */
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 380px; gap: 40px; }
 
        .card { background: white; padding: 40px; border-radius: 32px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 30px; }
        .section-label { font-size: 0.8rem; font-weight: 900; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; display: block; border-left: 4px solid var(--blue); padding-left: 15px; }
 
        .order-id-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
        .order-id-header h1 { font-size: 2rem; font-weight: 900; letter-spacing: -1.5px; }
        .order-id-header h1 span { color: var(--blue); }
 
        .status-badge { padding: 8px 18px; border-radius: 100px; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; }
        .status-placed { background: #eff6ff; color: #1e40af; }
        .status-delivered { background: #f1f5f9; color: #475569; }
 
        /* ===== DATA GRID ===== */
        .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 40px; }
        .info-item { padding: 20px; background: #f9fafb; border-radius: 20px; border: 1px solid #f3f4f6; }
        .info-lab { display: block; font-size: 0.75rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .info-val { font-weight: 850; font-size: 1.1rem; color: var(--text-dark); }
 
        /* ===== ITEM TABLE ===== */
        .item-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { text-align: left; padding: 15px 0; font-size: 0.75rem; font-weight: 800; color: var(--text-muted); border-bottom: 2px solid #f3f4f6; }
        td { padding: 18px 0; border-bottom: 1px solid #f3f4f6; font-weight: 700; }
        .total-row { padding-top: 30px; text-align: right; }
        .total-val { font-size: 2.2rem; font-weight: 900; color: #059669; }
 
        footer { background: #020617; padding: 60px 20px; color: #94a3b8; text-align: center; margin-top: 100px; grid-column: span 2; }
 
        @media (max-width: 1024px) {
            .container { grid-template-columns: 1fr; }
            footer { grid-column: span 1; }
        }
    </style>"""

content = content.replace('    </style>', missing_css)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed admin_view_order.html")
