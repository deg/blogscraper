"""Utility functions for scraping and processing URLs from various blogs.

Provides helper functions to fetch and parse blog URLs using BeautifulSoup,
and to normalize and store extracted data.

Usage:
    These functions are primarily used by blog-specific scraper modules to
    extract structured data from HTML pages.
"""

from datetime import datetime, timezone
from typing import Callable, List

from bs4 import BeautifulSoup

from blogscraper.types import URLDict
from blogscraper.utils.url_utils import get_html, normalize_url


def fetch_and_parse_urls(
    base_url: str, selector: str, source: str, date_extractor: Callable[[str], str]
) -> List[URLDict]:
    """Finds and extracts URLs from a given webpage using a CSS selector.

    Args:
        base_url (str): The base URL of the blog or archive page.
        selector (str): The CSS selector to locate article links.
        source (str): A string identifier for the source site.
        date_extractor (Callable[[str], str]): Function to extract a post's date from
                its URL.

    Returns:
        List[URLDict]: A list of extracted URLDict objects containing
        URLs, timestamps, and source information.

    """
    print(f"Fetching and parsing URLs from {base_url}")
    urls: List[URLDict] = []

    html = get_html(base_url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = soup.select(selector)

    for link in links:
        href = link.get("href")
        if isinstance(href, str):
            absolute_url = normalize_url(base_url, href)
            creation_date = date_extractor(absolute_url)
            url_dict: URLDict = {
                "url": absolute_url,
                "harvest_timestamp": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
                "source": source,
                "creation_date": creation_date,
            }
            urls.append(url_dict)

    return urls
