from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from blogscraper.types import URLDict


def scrape_thezvi() -> list[URLDict]:
    """
    Scrapes thezvi blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    url = "https://thezvi.wordpress.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all blog post links
    links = soup.select("h2.entry-title a")
    urls: list[URLDict] = []

    for link in links:
        href = link.get("href")
        if isinstance(href, str):
            url_dict: URLDict = {
                "url": href,
                "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "thezvi",
            }
            urls.append(url_dict)

    return urls
