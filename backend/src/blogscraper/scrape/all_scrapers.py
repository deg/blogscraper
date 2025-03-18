from blogscraper.types import Scraper

from .scrapers.cliffnotes import scrape_cliffnotes
from .scrapers.nathanbenaich import scrape_nathanbenaich
from .scrapers.simonwillison import scrape_simonwillison
from .scrapers.thezvi import scrape_thezvi

SCRAPERS = [
    Scraper(
        name="The Zvi", base_url="https://thezvi.wordpress.com/", function=scrape_thezvi
    ),
    Scraper(
        name="Simon Willison",
        base_url="https://simonwillison.net/",
        function=scrape_simonwillison,
    ),
    Scraper(
        name="Nathan Benaich",
        base_url="https://nathanbenaich.substack.com/archive?sort=new",
        function=scrape_nathanbenaich,
    ),
    Scraper(
        name="Cliffnotes",
        base_url="https://newsletter.cliffnotes.ai/",
        function=scrape_cliffnotes,
    ),
]
