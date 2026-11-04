from urllib.parse import urlparse

from src.scrapers.base import BaseScraper
from src.scrapers.books_toscrape import BooksToScrapeScraper
from src.scrapers.kabum import KabumScraper

# Cada site conhecido aponta para o scraper que sabe lê-lo.
SCRAPERS = {
    "books.toscrape.com": BooksToScrapeScraper,
    "kabum.com.br": KabumScraper,
}


def escolher_scraper(url: str) -> BaseScraper:
    dominio = urlparse(url).netloc.lower().removeprefix("www.")
    if dominio not in SCRAPERS:
        raise ValueError(f"Nenhum scraper disponível para o site: {dominio}")
    return SCRAPERS[dominio]()