from app import app
from models import User, Shopkeeper, Shop

with app.app_context():
    # Check shopkeeper 'lawget'
    sk = Shopkeeper.get_by_username('lawget')
    if sk:
        print(f"Shopkeeper: {sk['username']} (ID: {sk['id']})")
        shop = Shop.get_by_shopkeeper(sk['id'])
        if shop:
            print(f"Shop: {shop['name']} (ID: {shop['id']})")
            print(f"Logo Path: {shop['logo_path']}")
        else:
            print("No shop found for this shopkeeper.")
    else:
        print("Shopkeeper 'lawget' not found.")
