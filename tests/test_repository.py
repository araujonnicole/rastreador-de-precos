from src.database import repository
from src.scrapers.base import Produto

URL = "https://exemplo.com/produto/1"


def test_historico_guarda_precos_em_ordem(banco_temporario):
    repository.salvar_preco(Produto("Produto Teste", 100.0, URL))
    repository.salvar_preco(Produto("Produto Teste", 90.0, URL))

    historico = repository.listar_historico(URL)

    assert [linha["preco"] for linha in historico] == [100.0, 90.0]


def test_ultimo_preco_e_o_mais_recente(banco_temporario):
    repository.salvar_preco(Produto("Produto Teste", 100.0, URL))
    repository.salvar_preco(Produto("Produto Teste", 90.0, URL))

    assert repository.buscar_ultimo_preco(URL) == 90.0


def test_ultimo_preco_de_produto_novo_e_none(banco_temporario):
    assert repository.buscar_ultimo_preco(URL) is None


def test_produto_nao_e_duplicado(banco_temporario):
    repository.salvar_preco(Produto("Produto Teste", 100.0, URL))
    repository.salvar_preco(Produto("Produto Teste", 90.0, URL))

    conexao = repository.conectar()
    try:
        total = conexao.execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]
    finally:
        conexao.close()

    assert total == 1