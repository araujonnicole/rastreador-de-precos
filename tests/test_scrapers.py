import json

import pytest
import requests

from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.scrapers.kabum import KabumScraper


class RespostaFalsa:
    """Imita a resposta do site, sem acessar a internet."""

    def __init__(self, html):
        self.text = html
        self.encoding = None

    def raise_for_status(self):
        pass


def simular_pagina(monkeypatch, html):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: RespostaFalsa(html))


def montar_html_kabum(prices):
    next_data = {
        "props": {
            "pageProps": {"product": {"friendlyName": "ssd-teste", "prices": prices}}
        }
    }
    json_ld = {"@type": "Product", "name": "SSD Teste 480GB"}
    return (
        "<html><head>"
        f'<script type="application/ld+json">{json.dumps(json_ld)}</script>'
        f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>'
        "</head><body></body></html>"
    )


HTML_LIVRO = """
<html><body>
<h1>A Light in the Attic</h1>
<p class="price_color">£51.77</p>
</body></html>
"""


def test_scraper_do_livro_le_nome_e_preco(monkeypatch):
    simular_pagina(monkeypatch, HTML_LIVRO)

    produto = BooksToScrapeScraper().buscar_produto("https://books.toscrape.com/x")

    assert produto.nome == "A Light in the Attic"
    assert produto.preco == 51.77
    assert produto.moeda == "£"


def test_kabum_usa_o_preco_a_vista(monkeypatch):
    html = montar_html_kabum({"priceWithDiscount": 659.99, "price": 733.32})
    simular_pagina(monkeypatch, html)

    produto = KabumScraper().buscar_produto("https://www.kabum.com.br/produto/1")

    assert produto.preco == 659.99
    assert produto.nome == "SSD Teste 480GB"
    assert produto.moeda == "R$"


def test_kabum_usa_preco_normal_quando_nao_ha_desconto_a_vista(monkeypatch):
    simular_pagina(monkeypatch, montar_html_kabum({"price": 733.32}))

    produto = KabumScraper().buscar_produto("https://www.kabum.com.br/produto/1")

    assert produto.preco == 733.32


def test_kabum_sem_preco_gera_erro(monkeypatch):
    simular_pagina(monkeypatch, montar_html_kabum({}))

    with pytest.raises(ValueError):
        KabumScraper().buscar_produto("https://www.kabum.com.br/produto/1")


def test_kabum_pagina_sem_dados_gera_erro(monkeypatch):
    simular_pagina(monkeypatch, "<html><body>nada aqui</body></html>")

    with pytest.raises(ValueError):
        KabumScraper().buscar_produto("https://www.kabum.com.br/produto/1")