import re
from datetime import datetime

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import extend_posts_with_references, fetch_all_urls


def scrape_simonwillison(
    scraper: Scraper, existing_urls: list[URLDict]
) -> list[URLDict]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    blogpost_dicts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector="div#secondary ul li a",
        archive_selector="div.archive-links a",
        url_date_parser=extract_simonwillison_date,
    )

    return extend_posts_with_references(
        blogpost_dicts=blogpost_dicts,
        existing_urls=existing_urls,
        wrapping_selector="div.entryPage",
        ignore_remotes=[
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
    )


def extract_simonwillison_date(url: str) -> str:
    match = re.search(r"/(\d{4})/([A-Za-z]{3})/(\d{1,2})/", url)
    if match:
        year, month_str, day = match.groups()
        month = datetime.strptime(month_str, "%b").month
        dt = datetime(int(year), month, int(day))
        return datestring(dt)
    return "unknown"
