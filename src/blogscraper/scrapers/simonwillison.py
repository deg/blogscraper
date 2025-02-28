from datetime import datetime

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
    links = soup.select("article h2 a")
    urls = []

    for link in links:
        href = link.get("href")
        if href:
            urls.append(
                {
                    "url": href,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "simonwillison",
                }
            )

    return urls
