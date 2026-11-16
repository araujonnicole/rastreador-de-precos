from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


@dataclass
class Produto:
    nome: str
    preco: float
    url: str
    moeda: str = "£"


class BaseScraper(ABC):
    """Molde que todo scraper do projeto precisa seguir."""

    def baixar_html(self, url: str) -> str:
        resposta = requests.get(url, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        resposta.encoding = "utf-8"
        return resposta.text

    @abstractmethod
    def buscar_produto(self, url: str) -> Produto:
        """Acessa a página do produto e devolve nome, preço e link."""