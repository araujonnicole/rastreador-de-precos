from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[1] / "produtos.txt"


def carregar_urls() -> list[str]:
    urls = []
    for linha in ARQUIVO.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#"):
            urls.append(linha)
    return urls