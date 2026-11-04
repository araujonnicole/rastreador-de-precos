import pytest

from src.scrapers.base import BaseScraper, Produto
from src.services.tracker import ResultadoVerificacao, verificar_preco

URL = "https://exemplo.com/produto/1"


def criar_resultado(preco_anterior, preco_atual):
    produto = Produto(nome="Produto Teste", preco=preco_atual, url=URL)
    return ResultadoVerificacao(produto=produto, preco_anterior=preco_anterior)


class ScraperFalso(BaseScraper):
    def __init__(self, preco):
        self.preco = preco

    def buscar_produto(self, url):
        return Produto(nome="Produto Teste", preco=self.preco, url=url)


def test_primeira_coleta_nao_e_queda():
    resultado = criar_resultado(None, 100.0)
    assert resultado.caiu is False
    assert resultado.queda_percentual == 0.0


def test_preco_menor_e_queda():
    resultado = criar_resultado(100.0, 80.0)
    assert resultado.caiu is True
    assert resultado.queda_percentual == pytest.approx(20.0)


def test_preco_igual_nao_e_queda():
    resultado = criar_resultado(100.0, 100.0)
    assert resultado.caiu is False


def test_aumento_nao_e_queda():
    resultado = criar_resultado(100.0, 120.0)
    assert resultado.caiu is False
    assert resultado.queda_percentual == 0.0


def test_verificar_preco_compara_com_o_preco_anterior(banco_temporario):
    primeira = verificar_preco(ScraperFalso(100.0), URL)
    assert primeira.preco_anterior is None

    segunda = verificar_preco(ScraperFalso(80.0), URL)
    assert segunda.preco_anterior == 100.0
    assert segunda.caiu is True