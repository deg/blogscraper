from blogscraper.types import Scraper, URLDict

from ..scraper_utils import fetch_all_urls


def scrape_nathanbenaich(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    return fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector="div.portable-archive-list div:has(time)",
        html_a_selector='a[href][data-testid="post-preview-title"]',
        html_time_selector="time[datetime]",
    )
