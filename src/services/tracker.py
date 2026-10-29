from dataclasses import dataclass

from src.database.repository import buscar_ultimo_preco, salvar_preco
from src.scrapers.base import BaseScraper, Produto


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


def verificar_preco(scraper: BaseScraper, url: str) -> ResultadoVerificacao:
    preco_anterior = buscar_ultimo_preco(url)
    produto = scraper.buscar_produto(url)
    salvar_preco(produto)
    return ResultadoVerificacao(produto=produto, preco_anterior=preco_anterior)
