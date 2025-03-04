from datetime import datetime, timezone
from typing import Callable, List

from bs4 import BeautifulSoup

from blogscraper.types import URLDict
from blogscraper.utils.url_utils import get_html, normalize_url


def fetch_and_parse_urls(
    base_url: str, selector: str, source: str, date_extractor: Callable[[str], str]
) -> List[URLDict]:
    """
    Fetches and parses URLs from a given website using a CSS selector.

    Args:
        base_url (str): The base URL of the website.
        selector (str): The CSS selector to find links.
        source (str): The source identifier for the URLs.
        date_extractor (Callable[[str], str]): Extractor of posting date from URL.

    Returns:
        List[URLDict]: A list of URLDict objects with absolute URLs.
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
