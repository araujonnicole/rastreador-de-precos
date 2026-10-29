from src.config import (
    EMAIL_DESTINO,
    EMAIL_REMETENTE,
    SENDGRID_API_KEY,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)
from src.notifiers.base import Notifier
from src.notifiers.email_sendgrid import SendGridNotifier
from src.notifiers.telegram_bot import TelegramNotifier


def criar_notifiers() -> list[Notifier]:
    notifiers: list[Notifier] = []

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        notifiers.append(TelegramNotifier())

    if SENDGRID_API_KEY and EMAIL_REMETENTE and EMAIL_DESTINO:
        notifiers.append(SendGridNotifier())

    return notifiers