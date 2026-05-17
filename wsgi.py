"""
wsgi.py — Production entry point for Azhar-foodExp
Used by Gunicorn / any WSGI server for deployment
"""
# Initialize the database schema for production
import schema_init

from app import app

if __name__ == "__main__":
    app.run()
