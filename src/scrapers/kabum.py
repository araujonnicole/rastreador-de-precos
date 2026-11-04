import json

import requests
from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, Produto

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


class KabumScraper(BaseScraper):
    def buscar_produto(self, url: str) -> Produto:
        resposta = requests.get(url, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        resposta.encoding = "utf-8"

        sopa = BeautifulSoup(resposta.text, "html.parser")
        dados = self._ler_next_data(sopa)
        produto = dados["props"]["pageProps"]["product"]

        return Produto(
            nome=self._extrair_nome(sopa, produto),
            preco=self._extrair_preco(produto),
            url=url,
            moeda="R$",
        )

    @staticmethod
    def _ler_next_data(sopa: BeautifulSoup) -> dict:
        tag = sopa.find("script", id="__NEXT_DATA__")
        if tag is None:
            raise ValueError("Dados do produto (__NEXT_DATA__) não encontrados")
        return json.loads(tag.string)

    @staticmethod
    def _extrair_preco(produto: dict) -> float:
        precos = produto.get("prices") or {}
        valor = precos.get("priceWithDiscount") or precos.get("price")
        if valor is None:
            raise ValueError("Preço não encontrado nos dados do produto")
        return float(valor)

    @staticmethod
    def _extrair_nome(sopa: BeautifulSoup, produto: dict) -> str:
        for tag in sopa.find_all("script", type="application/ld+json"):
            try:
                dados = json.loads(tag.string)
            except (TypeError, json.JSONDecodeError):
                continue
            if (
                isinstance(dados, dict)
                and dados.get("@type") == "Product"
                and dados.get("name")
            ):
                return dados["name"]
        return produto.get("friendlyName", "Produto Kabum")