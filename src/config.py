import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

QUEDA_MINIMA_PERCENTUAL = float(os.getenv("QUEDA_MINIMA_PERCENTUAL", "5"))