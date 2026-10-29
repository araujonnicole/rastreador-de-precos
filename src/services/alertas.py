from src.notifiers.base import Notifier
from src.services.tracker import ResultadoVerificacao


def montar_mensagem(resultado: ResultadoVerificacao) -> str:
    produto = resultado.produto
    return (
        "📉 Queda de preço!\n\n"
        f"{produto.nome}\n"
        f"De £{resultado.preco_anterior:.2f} para £{produto.preco:.2f} "
        f"(-{resultado.queda_percentual:.1f}%)\n\n"
        f"{produto.url}"
    )


def notificar_queda(resultado: ResultadoVerificacao, notifier: Notifier) -> bool:
    if not resultado.caiu:
        return False
    notifier.enviar(montar_mensagem(resultado))
    return True