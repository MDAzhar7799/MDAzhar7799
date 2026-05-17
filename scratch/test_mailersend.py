import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = 'smtp.mailersend.net'
smtp_port = 587
smtp_user = 'MS_XwNkdY@test-68zxl273emm4j905.mlsender.net'
smtp_pass = 'mlsn.7448967837fd568925745ea11a87fb3f5cfb8b9a82f79077d3a06fa700c4c629'
sender_email = 'noreply@test-68zxl273emm4j905.mlsender.net'
to_email = 'mdazhark735@gmail.com'

msg = MIMEMultipart()
msg['From'] = f'FoodExpress Notifications <{sender_email}>'
msg['To'] = to_email
msg['Subject'] = 'Test - FoodExpress MailerSend Setup'

body = """<html>
<body style="font-family:Arial,sans-serif;padding:20px">
<h2 style="color:#16a34a">MailerSend Setup Successful!</h2>
<p>FoodExpress notification system is now connected to <strong>MailerSend</strong>.</p>
<p>Order Ready notifications will now be sent via this email service.</p>
<hr>
<p style="color:#888;font-size:12px">FoodExpress - LPU &amp; LawGate Food Platform</p>
</body>
</html>"""

msg.attach(MIMEText(body, 'html'))

try:
    print(f"Connecting to {smtp_server}:{smtp_port}...")
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        print("TLS started. Logging in...")
        server.login(smtp_user, smtp_pass)
        print("Logged in! Sending email...")
        server.send_message(msg)
    print(f"SUCCESS: Test email sent to {to_email}")
except Exception as e:
    print(f"ERROR: {str(e)}")
