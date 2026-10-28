from src.database.repository import criar_tabelas, listar_historico, salvar_preco
from src.scrapers.books_toscrape import BooksToScrapeScraper

URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

criar_tabelas()

scraper = BooksToScrapeScraper()
produto = scraper.buscar_produto(URL)
salvar_preco(produto)

print(f"Salvo: {produto.nome} - £{produto.preco}")
print("Histórico:")
for registro in listar_historico(URL):
    print(f"  {registro['data_coleta']} - £{registro['preco']}")