from src.database.repository import criar_tabelas
from src.notifiers.telegram_bot import TelegramNotifier
from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.services.alertas import notificar_queda
from src.services.tracker import verificar_preco

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

criar_tabelas()

scraper = BooksToScrapeScraper()
notifier = TelegramNotifier()

resultado = verificar_preco(scraper, URL)
produto = resultado.produto
print(f"{produto.nome}: £{produto.preco}")

if resultado.preco_anterior is None:
    print("Primeira coleta deste produto.")
elif notificar_queda(resultado, notifier):
    print("Queda detectada! Alerta enviado pelo Telegram.")
else:
    print(f"Sem queda (preço anterior: £{resultado.preco_anterior})")