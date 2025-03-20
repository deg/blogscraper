import re
from datetime import datetime
from typing import Callable

from bson import ObjectId

from blogscraper.types import Scraper
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import standard_scraper


def scrape_simonwillison(
    scraper: Scraper, status_callback: Callable[[str], None] | None = None
) -> list[ObjectId]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids
    """
    return standard_scraper(
        scraper=scraper,
        section_selector="div#secondary ul li a",
        archive_selector="div.archive-links a",
        url_date_parser=extract_simonwillison_date,
        wrapping_selector="div.entryPage",
        ignore_remotes=[
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
        status_callback=status_callback,
    )


def extract_simonwillison_date(url: str) -> str:
    match = re.search(r"/(\d{4})/([A-Za-z]{3})/(\d{1,2})/", url)
    if match:
        year, month_str, day = match.groups()
        month = datetime.strptime(month_str, "%b").month
        dt = datetime(int(year), month, int(day))
        return datestring(dt)
    return "unknown"
