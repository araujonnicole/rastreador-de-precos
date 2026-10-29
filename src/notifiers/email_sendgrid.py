import requests

from src.config import EMAIL_DESTINO, EMAIL_REMETENTE, SENDGRID_API_KEY
from src.notifiers.base import Notifier

URL_API = "https://api.sendgrid.com/v3/mail/send"


class SendGridNotifier(Notifier):
    def __init__(
        self,
        api_key=SENDGRID_API_KEY,
        remetente=EMAIL_REMETENTE,
        destino=EMAIL_DESTINO,
        assunto="Rastreador de Preços: queda de preço!",
    ):
        if not api_key or not remetente or not destino:
            raise ValueError(
                "Configure SENDGRID_API_KEY, EMAIL_REMETENTE e EMAIL_DESTINO no .env"
            )
        self.api_key = api_key
        self.remetente = remetente
        self.destino = destino
        self.assunto = assunto

    def enviar(self, mensagem: str) -> None:
        corpo = {
            "personalizations": [{"to": [{"email": self.destino}]}],
            "from": {"email": self.remetente},
            "subject": self.assunto,
            "content": [{"type": "text/plain", "value": mensagem}],
        }
        resposta = requests.post(
            URL_API,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=corpo,
            timeout=10,
        )
        resposta.raise_for_status()