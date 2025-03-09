from blogscraper.types import Scraper, URLDict

from ..scraper_utils import scrape_blog


def scrape_nathanbenaich(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = scraper.base_url
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "div.portable-archive-list div", False)
