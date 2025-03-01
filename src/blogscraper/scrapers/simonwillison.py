from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from blogscraper.types import URLDict


def scrape_simonwillison() -> list[URLDict]:
    """
    Scrapes Simon Willison's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    url = "https://simonwillison.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all blog post links
    links = soup.select("div#secondary ul li a")
    urls: list[URLDict] = []

    for link in links:
        href = link.get("href")
        if isinstance(href, str):
            url_dict: URLDict = {
                "url": href,
                "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "simonwillison",
            }
            urls.append(url_dict)

    return urls
