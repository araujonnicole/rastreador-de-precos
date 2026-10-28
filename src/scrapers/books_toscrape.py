import requests
from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, Produto


class BooksToScrapeScraper(BaseScraper):
    def buscar_produto(self, url: str) -> Produto:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        resposta.encoding = "utf-8"

        sopa = BeautifulSoup(resposta.text, "html.parser")

        nome = sopa.find("h1").get_text(strip=True)
        preco_texto = sopa.find("p", class_="price_color").get_text(strip=True)
        preco = float(preco_texto.replace("£", ""))

        return Produto(nome=nome, preco=preco, url=url)