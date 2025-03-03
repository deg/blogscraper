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
    return scrape_blog(base_url, "div.portable-archive-list div", False)


def scrape_cliffnotes() -> list[URLDict]:
    base_url = "https://newsletter.cliffnotes.ai/"
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "a", True)


def scrape_blog(base_url: str, selector: str, time_within_a: bool) -> list[URLDict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    archive_list = soup.select(selector)
    return extract_urls_from_archive(base_url, archive_list, time_within_a)


def extract_urls_from_archive(
    base_url: str, archive_list: list[Tag], time_within_a: bool
) -> list[URLDict]:
    """
    Extracts URLs and creation dates from the archive list.

    Args:
        base_url (str): The base URL of the blog archive.
        archive_list (list[Tag]): A list of HTML elements containing blog entries.
        time_within_a (bool): Indicates whether the time tag is within the anchor tag.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    urls: list[URLDict] = []

    for entry in archive_list:
        link = entry if time_within_a else entry.find("a", href=True)
        time_tag = entry.find("time", datetime=True)  # if not time_within_a else entry

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
            "source": base_url.split("//")[1].split("/")[0],
            "creation_date": creation_date_str,
        }
        urls.append(url_dict)

    return urls
