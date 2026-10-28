from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Produto:
    nome: str
    preco: float
    url: str


class BaseScraper(ABC):
    """Molde que todo scraper do projeto precisa seguir."""

    @abstractmethod
    def buscar_produto(self, url: str) -> Produto:
        """Acessa a página do produto e devolve nome, preço e link."""