from abc import ABC, abstractmethod


class Notifier(ABC):
    """Molde que todo notificador do projeto precisa seguir."""

    @abstractmethod
    def enviar(self, mensagem: str) -> None:
        """Envia uma mensagem de texto ao usuário."""