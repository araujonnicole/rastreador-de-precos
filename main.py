from src.database.repository import criar_tabelas
from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.services.tracker import verificar_preco

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

criar_tabelas()

scraper = BooksToScrapeScraper()
resultado = verificar_preco(scraper, URL)

produto = resultado.produto
print(f"{produto.nome}: £{produto.preco}")

if resultado.preco_anterior is None:
    print("Primeira coleta deste produto.")
elif resultado.caiu:
    print(
        f"QUEDA DE PREÇO! De £{resultado.preco_anterior} "
        f"para £{produto.preco} (-{resultado.queda_percentual:.1f}%)"
    )
else:
    print(f"Sem queda (preço anterior: £{resultado.preco_anterior})")