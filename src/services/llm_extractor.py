import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, field_validator

load_dotenv()

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
MAX_CHARS = 6000  # limite do texto enviado ao modelo
TENTATIVAS = 3
ESPERA_BASE = 4  # segundos; dobra a cada nova tentativa
CODIGOS_TEMPORARIOS = (429, 500, 503)  # erros do Google que passam sozinhos

PROMPT = """Você extrai dados de páginas de produtos de lojas online.
Abaixo está o texto visível da página de um produto. Devolva o nome do
produto e o preço à vista (o preço com desconto no PIX/boleto, quando houver).
Regras:
- "preco" deve ser um número com ponto decimal e sem símbolo de moeda (ex.: 1299.90).
- Ignore o preço riscado (antigo) e os valores de parcelas (ex.: "10 x R$ 73,33").
- Use apenas valores que aparecem no texto. Não invente.
- Se não encontrar o preço no texto, devolva preco 0.

TEXTO DA PÁGINA:
"""


class ProdutoExtraido(BaseModel):
    nome: str
    preco: float

    @field_validator("preco")
    @classmethod
    def preco_positivo(cls, valor):
        if valor <= 0:
            raise ValueError("preço não encontrado ou inválido")
        return valor


def _texto_visivel(html: str) -> str:
    """Pega só o texto que aparece na página (sem scripts, estilos e tags)."""
    sopa = BeautifulSoup(html, "html.parser")
    titulo = sopa.title.get_text(strip=True) if sopa.title else ""
    for tag in sopa(["script", "style", "noscript", "svg"]):
        tag.decompose()
    texto = sopa.get_text(" ", strip=True)
    if len(texto) > MAX_CHARS:
        # página grande: começa um pouco antes do primeiro "R$"
        pos = texto.find("R$")
        inicio = max(0, pos - 1500) if pos != -1 else 0
        texto = texto[inicio:inicio + MAX_CHARS]
    return f"TÍTULO: {titulo}\n{texto}"


def _formatos_do_preco(preco: float) -> list[str]:
    """Jeitos de o preço aparecer escrito: 1.299,90 / 1299,90 / 1,299.90 / 1299.90"""
    en = f"{preco:,.2f}"
    br = en.replace(",", "X").replace(".", ",").replace("X", ".")
    return [br, br.replace(".", ""), en, en.replace(",", "")]


def extrair_produto(html: str) -> ProdutoExtraido | None:
    """Plano B: pede ao LLM o nome e o preço. Devolve None se algo falhar."""
    chave = os.getenv("GEMINI_API_KEY")
    if not chave:
        raise RuntimeError("GEMINI_API_KEY não encontrada no .env")

    texto = _texto_visivel(html)
    client = genai.Client(api_key=chave)

    resposta_json = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = client.models.generate_content(
                model=MODELO,
                contents=PROMPT + texto,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProdutoExtraido,
                    temperature=0,
                ),
            )
            resposta_json = resposta.text
            break
        except Exception as erro:
            temporario = getattr(erro, "code", None) in CODIGOS_TEMPORARIOS
            if temporario and tentativa < TENTATIVAS:
                espera = ESPERA_BASE * 2 ** (tentativa - 1)
                print(f"[llm_extractor] Google indisponível "
                      f"(tentativa {tentativa}/{TENTATIVAS}); nova tentativa em {espera}s")
                time.sleep(espera)
                continue
            print(f"[llm_extractor] falha na extração: {erro}")
            return None

    try:
        produto = ProdutoExtraido.model_validate_json(resposta_json)
    except Exception as erro:
        print(f"[llm_extractor] falha na extração: {erro}")
        return None

    # trava anti-invenção: o preço devolvido precisa existir no texto enviado
    if not any(formato in texto for formato in _formatos_do_preco(produto.preco)):
        print(f"[llm_extractor] descartado: preço {produto.preco} não aparece no texto da página")
        return None

    return produto


if __name__ == "__main__":
    html_teste = """
    <html><head><title>Fone Bluetooth XYZ</title></head><body>
    <div class="produto">
      <h1>Fone Bluetooth XYZ</h1>
      <span class="preco-antigo">R$ 1.599,00</span>
      <span class="preco">R$ 1.299,90</span>
      <span>10x de R$ 129,99 sem juros</span>
    </div>
    </body></html>
    """
    print(extrair_produto(html_teste))