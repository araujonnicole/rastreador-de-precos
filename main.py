from src.scrapers.books_toscrape import BooksToScrapeScraper

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

scraper = BooksToScrapeScraper()
produto = scraper.buscar_produto(URL)

print(produto)
print(f"{produto.nome} custa £{produto.preco}")