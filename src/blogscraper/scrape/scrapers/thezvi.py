import re
from datetime import datetime

from bs4 import BeautifulSoup

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring
from blogscraper.utils.url_utils import get_html, normalize_url

from ..scraper_utils import fetch_and_parse_urls, fetch_multiple_pages

# Define a constant for the number of threads
MAX_WORKERS = 5


def scrape_thezvi(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes thezvi blog for URLs, including archived old posts.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = scraper.base_url
    selector = "h2.entry-title a"
    source = "thezvi"

    # Scrape the main page
    main_page_urls = fetch_and_parse_urls(
        base_url=base_url,
        selector=selector,
        source=source,
        date_extractor=extract_thezvi_date,
    )

    # Fetch additional URLs from the archive section
    html = get_html(base_url)
    if html is None:
        return main_page_urls

    soup = BeautifulSoup(html, "html.parser")
    search_section = soup.select_one("li#archives-2")
    if not search_section:
        return main_page_urls

    archive_urls = [
        normalize_url(base_url, href)
        for link in search_section.select("a")
        if isinstance(href := link.get("href"), str)
    ]

    # Use new fetch_multiple_pages function
    additional_urls = fetch_multiple_pages(
        archive_urls,
        lambda url: fetch_and_parse_urls(
            base_url=url,
            selector=selector,
            source=source,
            date_extractor=extract_thezvi_date,
        ),
    )

    return main_page_urls + additional_urls


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        dt = datetime(int(year), int(month), int(day))
        return datestring(dt)
    return "unknown"
