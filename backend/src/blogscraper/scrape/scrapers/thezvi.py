import re
from datetime import datetime
from typing import Callable

from bson import ObjectId

from blogscraper.types import Scraper
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import standard_scraper


def scrape_thezvi(
    scraper: Scraper, status_callback: Callable[[str], None] | None = None
) -> list[ObjectId]:
    """
    Scrapes The Zvi's blog for URLs, including archived old posts.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids
    """
    return standard_scraper(
        scraper=scraper,
        section_selector="h2.entry-title a",
        archive_selector="li#archives-2 a",
        url_date_parser=extract_thezvi_date,
        wrapping_selector="div#content",
        ignore_remotes=[
            "thezvi.substack.com",
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
        status_callback=status_callback,
    )


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        dt = datetime(int(year), int(month), int(day))
        return datestring(dt)
    return "unknown"
