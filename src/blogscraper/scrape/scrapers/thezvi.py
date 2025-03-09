import re
from datetime import datetime

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import fetch_all_urls

# Define a constant for the number of threads
MAX_WORKERS = 5


def scrape_thezvi(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes The Zvi's blog for URLs, including archived old posts.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    return fetch_all_urls(
        scraper,
        selector="h2.entry-title a",
        archive_selector="li#archives-2 a",
        date_extractor=extract_thezvi_date,
    )


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        dt = datetime(int(year), int(month), int(day))
        return datestring(dt)
    return "unknown"
