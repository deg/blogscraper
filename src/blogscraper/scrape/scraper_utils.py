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
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from blogscraper.types import URLDict
from blogscraper.utils.time_utils import datestring
from blogscraper.utils.url_utils import get_html, normalize_url


def extend_posts_with_references(
    blogpost_dicts: list[URLDict],
    wrapping_selector: str = "*",
    ignore_remotes: list[str] = [],
) -> list[URLDict]:
    """Extends a list of blog posts with extracted references from each post.

    Args:
        blogpost_dicts (list[URLDict]): A list of blog post metadata dictionaries.
        wrapping_selector (str, optional): CSS selector to scope link extraction.
            Defaults to "*", which selects all links on the page.
        ignore_remotes (list[str], optional): List of remote hosts to exclude
            from the extracted references. Defaults to an empty list.

    Returns:
        list[URLDict]: The original list of blog posts extended with extracted
        references with metada linking back to the original post URL and creation date.

    Notes:
        - Extracted links are filtered to include only remote references
          (external links).
        - Duplicate references are removed before inclusion.
    """
    ref_dicts: list[URLDict] = []
    for page in blogpost_dicts:
        references = references_from(
            url=page["url"],
            wrapping_selector=wrapping_selector,
            local=False,
            remote=True,
            ignore_remotes=ignore_remotes,
        )
        references = remove_duplicates(references)
        for ref in references:
            ref_dict: URLDict = {
                "url": ref,
                "harvest_timestamp": datestring(datetime.now()),
                "source": page["url"],
                "creation_date": page["creation_date"],
            }
            ref_dicts.append(ref_dict)

    return blogpost_dicts + ref_dicts


def remove_duplicates(strs: list[str]) -> list[str]:
    """Removes duplicate URLs while preserving order."""
    seen = set()
    return [str for str in strs if not (str in seen or seen.add(str))]


def references_from(
    url: str,
    wrapping_selector: str,
    local: bool = False,
    remote: bool = False,
    ignore_remotes: list[str] = [],
) -> list[str]:
    """Extracts filtered links from a webpage based on the wrapping selector.

    Args:
        url (str): The webpage URL to scrape.
        wrapping_selector (str): CSS selector for the container element.
        local (bool): Include links from the same site (matching host).
        remote (bool): Include external links.
        ignore_remotes (list[str]): List of remote hosts to ignore.

    Returns:
        list[str]: A filtered list of URLs.
    """
    html = get_html(url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Get the base host
    parsed_url = urlparse(url)
    base_host = parsed_url.netloc.lower()

    # Find all links within the wrapping selector
    container = soup.select_one(wrapping_selector)
    if not container:
        return []

    links = [a["href"] for a in container.find_all("a", href=True)]

    # Normalize URLs and filter based on `local`, `remote`, and `ignore_remotes`
    filtered_links = []
    for link in links:
        parsed_link = urlparse(link)
        if not parsed_link.netloc:  # Relative URL
            full_link = urljoin(url, link)
            is_local = True  # Relative links are always local
        else:
            full_link = link
            host = parsed_link.netloc.lower()
            is_local = host == base_host
            if host in ignore_remotes:
                continue

        if (local and is_local) or (remote and not is_local):
            filtered_links.append(full_link)

    return filtered_links


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
