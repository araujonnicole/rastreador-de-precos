import logging
import sys
from pathlib import Path

from src.config import QUEDA_MINIMA_PERCENTUAL
from src.database.repository import criar_tabelas
from src.notifiers.factory import criar_notifiers
from src.produtos import carregar_urls
from src.scrapers.registry import escolher_scraper
from src.services.alertas import notificar_queda
from src.services.tracker import verificar_preco

RAIZ = Path(__file__).resolve().parent
logger = logging.getLogger("rastreador")


def configurar_logs() -> None:
    pasta_logs = RAIZ / "logs"
    pasta_logs.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(pasta_logs / "rastreador.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def verificar_url(url: str, notifiers: list) -> bool:
    """Verifica um produto. Devolve True se deu certo, False se falhou."""
    try:
        scraper = escolher_scraper(url)
        resultado = verificar_preco(scraper, url)
    except Exception:
        logger.exception("Falha ao verificar o preço de %s", url)
        return False

    produto = resultado.produto
    moeda = produto.moeda
    logger.info("%s: %s %.2f", produto.nome, moeda, produto.preco)

    if resultado.preco_anterior is None:
        logger.info("Primeira coleta deste produto.")
    elif notificar_queda(resultado, notifiers):
        logger.info(
            "Queda de %.1f%% detectada! Alertas enviados.", resultado.queda_percentual
        )
    elif resultado.caiu:
        logger.info(
            "Queda de %.1f%%, abaixo do mínimo de %s%%. Sem alerta.",
            resultado.queda_percentual,
            QUEDA_MINIMA_PERCENTUAL,
        )
    else:
        logger.info("Sem queda (preço anterior: %s %.2f)", moeda, resultado.preco_anterior)
    return True


def main() -> int:
    configurar_logs()
    criar_tabelas()

    notifiers = criar_notifiers()
    if not notifiers:
        logger.warning("Nenhum canal de notificação configurado no .env")

    urls = carregar_urls()
    if not urls:
        logger.warning("Nenhum produto encontrado em produtos.txt")
        return 1

    falhas = 0
    for url in urls:
        if not verificar_url(url, notifiers):
            falhas += 1

    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())