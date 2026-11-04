import pytest

from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.scrapers.kabum import KabumScraper
from src.scrapers.registry import escolher_scraper


def test_escolhe_o_scraper_pelo_dominio():
    livro = escolher_scraper("https://books.toscrape.com/catalogue/x")
    kabum = escolher_scraper("https://www.kabum.com.br/produto/1/x")

    assert isinstance(livro, BooksToScrapeScraper)
    assert isinstance(kabum, KabumScraper)


def test_site_desconhecido_gera_erro():
    with pytest.raises(ValueError):
        escolher_scraper("https://loja-desconhecida.com/produto")