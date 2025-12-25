import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # load .env file


# ===============================
# TELEGRAM CONFIG
# ===============================
TELEGRAM_BOT_TOKEN = os.getenv("<kunwarimaytokendito>")
TELEGRAM_CHAT_ID = os.getenv("-<ditoden>")

def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Error:", e)


# ===============================
# SMTP (GMAIL) CONFIG
# ===============================
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("SMTP Error:", e)


# ===============================
# LOG HELPER
# ===============================
def log_event(title, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"<b>{title}</b>\n\n{details}\n\n⏰ {timestamp}"
    send_to_telegram(message)
