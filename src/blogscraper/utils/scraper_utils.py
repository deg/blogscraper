from datetime import datetime, timezone
from typing import List

import requests
from bs4 import BeautifulSoup

from blogscraper.types import URLDict
from blogscraper.utils.url_utils import normalize_url


def fetch_and_parse_urls(base_url: str, selector: str, source: str) -> List[URLDict]:
    """
    Fetches and parses URLs from a given website using a CSS selector.

    Args:
        base_url (str): The base URL of the website.
        selector (str): The CSS selector to find links.
        source (str): The source identifier for the URLs.

    Returns:
        List[URLDict]: A list of URLDict objects with absolute URLs.
    """
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.select(selector)
    urls: List[URLDict] = []

    for link in links:
        href = link.get("href")
        if isinstance(href, str):
            absolute_url = normalize_url(base_url, href)
            url_dict: URLDict = {
                "url": absolute_url,
                "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": source,
            }
            urls.append(url_dict)

    return urls
