import requests

from src.config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
from src.notifiers.base import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, token=TELEGRAM_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        if not token or not chat_id:
            raise ValueError(
                "Configure TELEGRAM_TOKEN e TELEGRAM_CHAT_ID no arquivo .env"
            )
        self.token = token
        self.chat_id = chat_id

    def enviar(self, mensagem: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        resposta = requests.post(
            url,
            json={"chat_id": self.chat_id, "text": mensagem},
            timeout=10,
        )
        resposta.raise_for_status()