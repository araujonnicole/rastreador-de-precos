from dataclasses import dataclass

from src.database.repository import buscar_ultimo_preco, salvar_preco
from src.scrapers.base import BaseScraper, Produto
from src.services.llm_extractor import extrair_produto

# Erros de "não consegui ler a página" (erros de rede ficam de fora de propósito)
ERROS_DE_LEITURA = (ValueError, KeyError, TypeError)


@dataclass
class ResultadoVerificacao:
    produto: Produto
    preco_anterior: float | None

    @property
    def caiu(self) -> bool:
        return (
            self.preco_anterior is not None
            and self.produto.preco < self.preco_anterior
        )

    @property
    def queda_percentual(self) -> float:
        if not self.caiu:
            return 0.0
        return (self.preco_anterior - self.produto.preco) / self.preco_anterior * 100


def _plano_b_llm(scraper: BaseScraper, url: str) -> Produto | None:
    html = scraper.baixar_html(url)
    extraido = extrair_produto(html)
    if extraido is None:
        return None
    return Produto(nome=extraido.nome, preco=extraido.preco, url=url, moeda="R$")


def verificar_preco(scraper: BaseScraper, url: str) -> ResultadoVerificacao:
    preco_anterior = buscar_ultimo_preco(url)
    try:
        produto = scraper.buscar_produto(url)
    except ERROS_DE_LEITURA as erro:
        print(f"[verificar_preco] scraping falhou ({erro}); tentando o plano B com LLM")
        produto = _plano_b_llm(scraper, url)
        if produto is None:
            raise  # o LLM também falhou: devolve o erro original, como antes
    salvar_preco(produto)
    return ResultadoVerificacao(produto=produto, preco_anterior=preco_anterior)