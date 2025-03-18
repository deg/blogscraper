import re
from datetime import datetime

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import extend_posts_with_references, fetch_all_urls

# Define a constant for the number of threads
MAX_WORKERS = 5


def scrape_thezvi(scraper: Scraper, existing_urls: list[URLDict]) -> list[URLDict]:
    """
    Scrapes The Zvi's blog for URLs, including archived old posts.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    blogpost_dicts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector="h2.entry-title a",
        archive_selector="li#archives-2 a",
        url_date_parser=extract_thezvi_date,
    )

    return extend_posts_with_references(
        blogpost_dicts=blogpost_dicts,
        existing_urls=existing_urls,
        wrapping_selector="div#content",
        ignore_remotes=[
            "thezvi.substack.com",
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
    )


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        dt = datetime(int(year), int(month), int(day))
        return datestring(dt)
    return "unknown"
