import logging
import sys
from pathlib import Path

from src.config import QUEDA_MINIMA_PERCENTUAL
from src.database.repository import criar_tabelas
from src.notifiers.factory import criar_notifiers
from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.services.alertas import notificar_queda
from src.services.tracker import verificar_preco

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

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


def main() -> int:
    configurar_logs()
    criar_tabelas()

    notifiers = criar_notifiers()
    if not notifiers:
        logger.warning("Nenhum canal de notificação configurado no .env")

    try:
        resultado = verificar_preco(BooksToScrapeScraper(), URL)
    except Exception:
        logger.exception("Falha ao verificar o preço de %s", URL)
        return 1

    produto = resultado.produto
    logger.info("%s: £%s", produto.nome, produto.preco)

    if resultado.preco_anterior is None:
        logger.info("Primeira coleta deste produto.")
    elif notificar_queda(resultado, notifiers):
        logger.info("Queda de %.1f%% detectada! Alertas enviados.", resultado.queda_percentual)
    elif resultado.caiu:
        logger.info(
            "Queda de %.1f%%, abaixo do mínimo de %s%%. Sem alerta.",
            resultado.queda_percentual,
            QUEDA_MINIMA_PERCENTUAL,
        )
    else:
        logger.info("Sem queda (preço anterior: £%s)", resultado.preco_anterior)

    return 0


if __name__ == "__main__":
    sys.exit(main())
    