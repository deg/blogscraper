import re
from datetime import datetime

from blogscraper.types import URLDict
from blogscraper.utils.scraper_utils import fetch_and_parse_urls


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day)).isoformat()
    return ""


def scrape_thezvi() -> list[URLDict]:
    """
    Scrapes thezvi blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    return fetch_and_parse_urls(
        base_url="https://thezvi.wordpress.com/",
        selector="h2.entry-title a",
        source="thezvi",
        date_extractor=extract_thezvi_date,
    )
