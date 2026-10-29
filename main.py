from src.config import QUEDA_MINIMA_PERCENTUAL
from src.database.repository import criar_tabelas
from src.notifiers.factory import criar_notifiers
from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.services.alertas import notificar_queda
from src.services.tracker import verificar_preco

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

criar_tabelas()

scraper = BooksToScrapeScraper()
notifiers = criar_notifiers()
if not notifiers:
    print("Aviso: nenhum canal de notificação configurado no .env")

resultado = verificar_preco(scraper, URL)
produto = resultado.produto
print(f"{produto.nome}: £{produto.preco}")

if resultado.preco_anterior is None:
    print("Primeira coleta deste produto.")
elif notificar_queda(resultado, notifiers):
    print(f"Queda de {resultado.queda_percentual:.1f}% detectada! Alertas enviados.")
elif resultado.caiu:
    print(
        f"Queda de {resultado.queda_percentual:.1f}%, abaixo do mínimo de "
        f"{QUEDA_MINIMA_PERCENTUAL}%. Sem alerta."
    )
else:
    print(f"Sem queda (preço anterior: £{resultado.preco_anterior})")