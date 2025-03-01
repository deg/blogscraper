import re
from datetime import datetime

from blogscraper.types import URLDict
from blogscraper.utils.scraper_utils import fetch_and_parse_urls


def extract_simonwillison_date(url: str) -> str:
    match = re.search(r"/(\d{4})/([A-Za-z]{3})/(\d{1,2})/", url)
    if match:
        year, month_str, day = match.groups()
        month = datetime.strptime(month_str, "%b").month
        return datetime(int(year), month, int(day)).isoformat()
    return ""


def scrape_simonwillison() -> list[URLDict]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    return fetch_and_parse_urls(
        base_url="https://simonwillison.net/",
        selector="div#secondary ul li a",
        source="simonwillison",
        date_extractor=extract_simonwillison_date,
    )
