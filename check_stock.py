import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

PRODUCT_URL  = "https://www.spigen.com.tr/arama/ACH02589"
PRODUCT_NAME = "Spigen ACH02589 45W + USB-C Cable"

GMAIL_USER        = os.environ["GMAIL_USER"]
GMAIL_PASS        = os.environ["GMAIL_PASS"]
NOTIFY_EMAIL      = os.environ["NOTIFY_EMAIL"]
TELEGRAM_TOKEN    = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID  = os.environ["TELEGRAM_CHAT_ID"]

OUT_OF_STOCK_TEXT = "Seçtiğiniz kriterlere uygun ürün bulunamamıştır."

def check_stock():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "tr-TR,tr;q=0.9",
    }
    try:
        resp = requests.get(PRODUCT_URL, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[HATA] Siteye bağlanılamadı: {e}")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text()

    if OUT_OF_STOCK_TEXT in page_text:
        print("❌ Ürün hâlâ stokta yok.")
        return False

    print("✅ ÜRÜN STOĞA GİRDİ!")
    return True

def send_email(in_stock):
    if in_stock:
        subject = f"✅ ÜRÜN STOĞA GİRDİ: {PRODUCT_NAME}"
        body = f"""Merhaba,

✅ TAKİP ETTİĞİN ÜRÜN STOĞA GİRDİ!

📦 Ürün: {PRODUCT_NAME}
🔗 Satın almak için: {PRODUCT_URL}

Hemen al, stok tükenmeden!

──────────────────────────
Bu bildirim otomatik stok takip botu tarafından gönderilmiştir.
"""
    else:
        subject = f"❌ Ürün Hâlâ Stokta Yok: {PRODUCT_NAME}"
        body = f"""Merhaba,

❌ Takip ettiğin ürün henüz stoğa girmedi.

📦 Ürün: {PRODUCT_NAME}
🔗 Ürün linki: {PRODUCT_URL}

Bot kontrol etmeye devam ediyor, stoğa girdiğinde haber verecek.

──────────────────────────
Bu bildirim otomatik stok takip botu tarafından gönderilmiştir.
"""

    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, NOTIFY_EMAIL, msg.as_string())

    print(f"📧 E-posta gönderildi → {NOTIFY_EMAIL}")

def send_telegram(in_stock):
    if in_stock:
        message = (
            f"✅ *ÜRÜN STOĞA GİRDİ!*\n\n"
            f"📦 *{PRODUCT_NAME}*\n\n"
            f"🛒 Hemen satın al:\n{PRODUCT_URL}"
        )
    else:
        message = (
            f"❌ *Ürün Hâlâ Stokta Yok*\n\n"
            f"📦 *{PRODUCT_NAME}*\n\n"
            f"🔍 Bot kontrol etmeye devam ediyor..."
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown",
    }

    resp = requests.post(url, json=payload, timeout=10)
    if resp.ok:
        print("📱 Telegram bildirimi gönderildi.")
    else:
        print(f"[HATA] Telegram gönderilemedi: {resp.text}")

if __name__ == "__main__":
    in_stock = check_stock()
    send_email(in_stock)
    send_telegram(in_stock)
