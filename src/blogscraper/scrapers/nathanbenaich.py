from datetime import datetime

from bs4 import BeautifulSoup, Tag

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring
from blogscraper.utils.url_utils import get_html, normalize_url


def scrape_nathanbenaich(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    base_url = scraper.base_url
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "div.portable-archive-list div", False)


def scrape_cliffnotes(scraper: Scraper) -> list[URLDict]:
    base_url = scraper.base_url
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "a", True)


def scrape_blog(base_url: str, selector: str, time_within_a: bool) -> list[URLDict]:
    html = get_html(base_url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
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
        creation_date = datetime.fromisoformat(creation_date_raw)
        creation_date_str = datestring(creation_date)

        url_dict: URLDict = {
            "url": absolute_url,
            "harvest_timestamp": datestring(datetime.now()),
            "source": base_url.split("//")[1].split("/")[0],
            "creation_date": creation_date_str,
        }
        urls.append(url_dict)

    return urls
