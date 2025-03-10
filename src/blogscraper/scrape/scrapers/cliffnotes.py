from blogscraper.types import Scraper, URLDict

from ..scraper_utils import fetch_all_urls


def scrape_cliffnotes(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes Cliffnotes's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    return fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector='a[href^="/p/"]:has(time)',
        html_time_selector="time[datetime]",
    )
