from blogscraper.types import URLDict
from blogscraper.utils.scraper_utils import fetch_and_parse_urls


def scrape_simonwillison() -> list[URLDict]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = "https://simonwillison.net/"
    selector = "div#secondary ul li a"
    source = "simonwillison"
    return fetch_and_parse_urls(base_url, selector, source)
