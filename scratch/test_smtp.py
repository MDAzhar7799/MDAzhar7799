import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Path to the .env file in the lpu-food python directory
dotenv_path = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\.env'
load_dotenv(dotenv_path)

SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')

print(f"Testing with:")
print(f"Server: {SMTP_SERVER}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
# print(f"Pass: {SMTP_PASS}") # Don't print password

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        print("SUCCESS: SMTP Login successful!")
except Exception as e:
    print(f"FAILED: {e}")
