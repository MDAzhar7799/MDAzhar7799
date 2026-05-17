"""
wsgi.py — Production entry point for FoodExpress
Used by Gunicorn / any WSGI server for deployment
"""
from app import app

if __name__ == "__main__":
    app.run()
