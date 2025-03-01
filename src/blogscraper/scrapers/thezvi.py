from blogscraper.types import URLDict
from blogscraper.utils.scraper_utils import fetch_and_parse_urls


def scrape_thezvi() -> list[URLDict]:
    """
    Scrapes thezvi blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = "https://thezvi.wordpress.com/"
    selector = "h2.entry-title a"
    source = "thezvi"
    return fetch_and_parse_urls(base_url, selector, source)
