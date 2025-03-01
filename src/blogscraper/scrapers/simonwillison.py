from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from blogscraper.types import URLDict
from blogscraper.utils.url_utils import normalize_url


def scrape_simonwillison() -> list[URLDict]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = "https://simonwillison.net/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all blog post links
    links = soup.select("div#secondary ul li a")
    urls: list[URLDict] = []

    for link in links:
        href = link.get("href")
        if isinstance(href, str):
            absolute_url = normalize_url(base_url, href)
            url_dict: URLDict = {
                "url": absolute_url,
                "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "simonwillison",
            }
            urls.append(url_dict)

    return urls
