"""Utility functions for scraping and processing URLs from various blogs.

Provides helper functions to fetch and parse blog URLs using BeautifulSoup,
and to normalize and store extracted data.

Usage:
    These functions are primarily used by blog-specific scraper modules to
    extract structured data from HTML pages.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable

from bs4 import BeautifulSoup, Tag

from blogscraper.types import URLDict
from blogscraper.utils.time_utils import datestring
from blogscraper.utils.url_utils import get_html, normalize_url


def fetch_all_urls(
    base_url: str,
    source_name: str,
    selector: str,
    archive_selector: str | None = None,
    html_a_selector: str | None = None,
    html_time_selector: str | None = None,
    url_date_parser: Callable[[str], str] | None = None,
) -> list[URLDict]:
    """
    Fetches URLs from both the main page and archive pages.

    Args:
        base_url (str): Base URL of the blog collection.
        selector (str): CSS selector for extracting links from pages.
        archive_selector (str): CSS selector for finding archive links.
        date_extractor (Callable[[str], str]): Function to extract date from URL.

    Returns:
        list[URLDict]: List of extracted URLs from main and archive pages.
    """

    print(f"Fetching and parsing URLs from {base_url}")

    # Collect all pages (main + archives)
    pages_to_fetch = [base_url]
    if archive_selector:
        pages_to_fetch += extract_archive_links(base_url, archive_selector)

    # Fetch all pages in parallel
    return fetch_multiple_pages(
        pages_to_fetch,
        lambda url: fetch_and_parse_urls(
            base_url=url,
            source=source_name,
            selector=selector,
            html_a_selector=html_a_selector,
            html_time_selector=html_time_selector,
            url_date_parser=url_date_parser,
        ),
    )


def extract_archive_links(base_url: str, archive_selector: str) -> list[str]:
    """
    Extracts archive page URLs from a site's main page.

    Args:
        base_url (str): The base URL of the site.
        archive_selector (str): CSS selector for finding archive links.

    Returns:
        list[str]: A list of archive URLs.
    """
    html = get_html(base_url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    return [
        normalize_url(base_url, href)
        for link in soup.select(archive_selector)
        if isinstance(href := link.get("href"), str)
    ]


def fetch_and_parse_urls(
    base_url: str,
    selector: str,
    source: str,
    html_a_selector: str | None = None,
    html_time_selector: str | None = None,
    url_date_parser: Callable[[str], str] | None = None,
) -> list[URLDict]:
    """Finds and extracts URLs from a given webpage using a CSS selector.

    Args:
        base_url (str): The base URL of the blog or archive page.
        selector (str): The CSS selector to locate article links.
        source (str): A string identifier for the source site.
        date_extractor (Callable[[str], str]): Function to extract a post's date from
                its URL.

    Returns:
        list[URLDict]: A list of extracted URLDict objects containing
        URLs, timestamps, and source information.
    """
    urls: list[URLDict] = []

    html = get_html(base_url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    posts = soup.select(selector)

    for post in posts:
        link: Tag = post
        if html_a_selector:
            selected_link = post.select_one(html_a_selector)
            if not selected_link:
                continue
            link = selected_link
        href = link.get("href")
        if not isinstance(href, str):
            continue
        absolute_url = normalize_url(base_url, href)
        creation_date_raw = None
        if url_date_parser:
            creation_date_raw = url_date_parser(absolute_url)
        if html_time_selector:
            time_tag = post.select_one(html_time_selector)
            if not isinstance(time_tag, Tag):
                continue
            if isinstance(tag_datetime := time_tag.get("datetime"), str):
                creation_date_raw = tag_datetime
        if not isinstance(creation_date_raw, str):
            continue
        creation_date = datetime.fromisoformat(creation_date_raw)
        if not creation_date:
            continue
        creation_date_str = datestring(creation_date)
        if not creation_date_str:
            continue
        url_dict: URLDict = {
            "url": absolute_url,
            "harvest_timestamp": datestring(datetime.now()),
            "source": source,
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
