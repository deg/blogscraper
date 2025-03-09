"""Utility functions for scraping and processing URLs from various blogs.

Provides helper functions to fetch and parse blog URLs using BeautifulSoup,
and to normalize and store extracted data.

Usage:
    These functions are primarily used by blog-specific scraper modules to
    extract structured data from HTML pages.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable, List

from bs4 import BeautifulSoup, Tag

from blogscraper.types import URLDict
from blogscraper.utils.time_utils import datestring
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
                "harvest_timestamp": datestring(datetime.now()),
                "source": source,
                "creation_date": creation_date,
            }
            urls.append(url_dict)

    return urls


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


def fetch_multiple_pages(
    urls: list[str],
    scraper_function: Callable[[str], list[URLDict]],
    max_workers: int = 5,
) -> list[URLDict]:
    """
    Fetch multiple pages in parallel using ThreadPoolExecutor.

    Args:
        urls (list[str]): List of page URLs to scrape.
        scraper_function (Callable[[str], list[URLDict]]):
            Function that takes a URL and returns a list of extracted URLs.
        max_workers (int): Number of parallel workers (default: 5).

    Returns:
        list[URLDict]: Aggregated list of extracted URLs from all pages.
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(scraper_function, url): url for url in urls}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Error fetching {url}: {e}")

    return results
