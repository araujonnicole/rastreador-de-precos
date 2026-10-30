import logging

from src.config import QUEDA_MINIMA_PERCENTUAL
from src.notifiers.base import Notifier
from src.services.tracker import ResultadoVerificacao

logger = logging.getLogger(__name__)


def montar_mensagem(resultado: ResultadoVerificacao) -> str:
    produto = resultado.produto
    return (
        "📉 Queda de preço!\n\n"
        f"{produto.nome}\n"
        f"De £{resultado.preco_anterior:.2f} para £{produto.preco:.2f} "
        f"(-{resultado.queda_percentual:.1f}%)\n\n"
        f"{produto.url}"
    )


def notificar_queda(
    resultado: ResultadoVerificacao,
    notifiers: list[Notifier],
    queda_minima: float = QUEDA_MINIMA_PERCENTUAL,
) -> bool:
    if not resultado.caiu or resultado.queda_percentual < queda_minima:
        return False

    mensagem = montar_mensagem(resultado)
    for notifier in notifiers:
        try:
            notifier.enviar(mensagem)
        except Exception as erro:
            logger.error(
                "Falha em %s: %s", type(notifier).__name__, type(erro).__name__
            )
    return True