from src.notifiers.base import Notifier
from src.scrapers.base import Produto
from src.services.alertas import montar_mensagem, notificar_queda
from src.services.tracker import ResultadoVerificacao


class NotifierFalso(Notifier):
    def __init__(self):
        self.mensagens = []

    def enviar(self, mensagem):
        self.mensagens.append(mensagem)


class NotifierQuebrado(Notifier):
    def enviar(self, mensagem):
        raise RuntimeError("falhou")


def criar_resultado(preco_anterior, preco_atual, moeda="R$"):
    produto = Produto(
        nome="SSD Teste",
        preco=preco_atual,
        url="https://exemplo.com/p",
        moeda=moeda,
    )
    return ResultadoVerificacao(produto=produto, preco_anterior=preco_anterior)


def test_queda_acima_do_minimo_envia_alerta():
    notifier = NotifierFalso()
    enviou = notificar_queda(criar_resultado(100.0, 80.0), [notifier], queda_minima=5)
    assert enviou is True
    assert len(notifier.mensagens) == 1


def test_queda_abaixo_do_minimo_nao_envia():
    notifier = NotifierFalso()
    enviou = notificar_queda(criar_resultado(100.0, 98.0), [notifier], queda_minima=5)
    assert enviou is False
    assert notifier.mensagens == []


def test_preco_igual_nao_envia():
    notifier = NotifierFalso()
    enviou = notificar_queda(criar_resultado(100.0, 100.0), [notifier], queda_minima=5)
    assert enviou is False
    assert notifier.mensagens == []


def test_aumento_de_preco_nao_envia():
    notifier = NotifierFalso()
    enviou = notificar_queda(criar_resultado(100.0, 130.0), [notifier], queda_minima=5)
    assert enviou is False
    assert notifier.mensagens == []


def test_primeira_coleta_nao_envia():
    notifier = NotifierFalso()
    enviou = notificar_queda(criar_resultado(None, 100.0), [notifier], queda_minima=5)
    assert enviou is False
    assert notifier.mensagens == []


def test_falha_em_um_canal_nao_impede_os_outros():
    bom = NotifierFalso()
    resultado = criar_resultado(100.0, 50.0)
    enviou = notificar_queda(resultado, [NotifierQuebrado(), bom], queda_minima=5)
    assert enviou is True
    assert len(bom.mensagens) == 1


def test_mensagem_usa_a_moeda_do_produto():
    mensagem = montar_mensagem(criar_resultado(100.0, 80.0, moeda="R$"))
    assert "R$ 100.00" in mensagem
    assert "R$ 80.00" in mensagem
    assert "SSD Teste" in mensagem
    assert "https://exemplo.com/p" in mensagem