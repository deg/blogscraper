from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, Tag

from blogscraper.types import URLDict
from blogscraper.utils.url_utils import normalize_url


def scrape_nathanbenaich() -> list[URLDict]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = "https://nathanbenaich.substack.com/archive?sort=new"
    print(f"Fetching and parsing URLs from {base_url}")

    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    archive_list = soup.select("div.portable-archive-list div")
    return extract_urls_from_archive(base_url, archive_list)


def extract_urls_from_archive(base_url: str, archive_list: list[Tag]) -> list[URLDict]:
    """
    Extracts URLs and creation dates from the archive list.

    Args:
        base_url (str): The base URL of the blog archive.
        archive_list (list[Tag]): A list of HTML elements containing blog entries.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    urls: list[URLDict] = []

    for entry in archive_list:
        link = entry.find("a", href=True)
        time_tag = entry.find("time", datetime=True)

        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if not isinstance(href, str):
            continue
        if not isinstance(time_tag, Tag):
            continue

        creation_date_raw = time_tag.get("datetime")
        if not isinstance(creation_date_raw, str):
            continue

        absolute_url = normalize_url(base_url, href)

        creation_date = datetime.fromisoformat(creation_date_raw.replace("Z", "+00:00"))
        creation_date_str = creation_date.strftime("%Y-%m-%dT%H:%M:%S%z")

        url_dict: URLDict = {
            "url": absolute_url,
            "harvest_timestamp": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S%z"
            ),
            "source": "nathanbenaich",
            "creation_date": creation_date_str,
        }
        urls.append(url_dict)

    return urls
