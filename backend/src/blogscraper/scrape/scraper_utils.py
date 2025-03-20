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
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from bson import ObjectId
from degel_python_utils import setup_logger

from blogscraper.content_viewer import show_page_content
from blogscraper.types import Scraper, URLDict
from blogscraper.utils.mongodb_helpers import add_post, get_documents
from blogscraper.utils.time_utils import datestring
from blogscraper.utils.url_utils import get_html, normalize_url

logger = setup_logger(__name__)
# pylint: disable=logging-format-interpolation


def standard_scraper(
    scraper: Scraper,
    section_selector: str,
    wrapping_selector: str,
    ignore_remotes: list[str],
    archive_selector: str | None = None,
    html_a_selector: str | None = None,
    html_time_selector: str | None = None,
    url_date_parser: Callable[[str], str] | None = None,
    status_callback: Callable[[str], None] | None = None,
) -> list[ObjectId]:
    """
    Scrapes a blog post website for posts and references.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids
    """

    if status_callback:
        status_callback(f"{scraper.name}: Fetching post URLs")
    new_posts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector=section_selector,
        archive_selector=archive_selector,
        html_a_selector=html_a_selector,
        html_time_selector=html_time_selector,
        url_date_parser=url_date_parser,
    )

    if status_callback:
        status_callback(f"{scraper.name}: Finding reference URLs")
    new_refs = extend_posts_with_references(
        doc_ids=new_posts,
        wrapping_selector=wrapping_selector,
        ignore_remotes=ignore_remotes,
    )
    return new_posts + new_refs


def extend_posts_with_references(
    doc_ids: list[ObjectId],
    wrapping_selector: str = "*",
    ignore_remotes: list[str] = [],
) -> list[ObjectId]:
    """Extends a list of blog posts with extracted references from each post.

    Args:
        doc_id (list[ObjectId]): A list of MongoDB document ids to explore.
        existing_urls: (list[URLDict]): URLs that we've previously stored.
        wrapping_selector (str, optional): CSS selector to scope link extraction.
            Defaults to "*", which selects all links on the page.
        ignore_remotes (list[str], optional): List of remote hosts to exclude
            from the extracted references. Defaults to an empty list.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids

    Side effects:
       Adds all newly-discovered pages to the MongoDB.
    Notes:
        - Extracted links are filtered to include only remote references
          (external links).
        - Duplicate references are removed before inclusion.

    """
    ids = []
    blogpost_dicts = get_documents(doc_ids)

    for page in blogpost_dicts:
        references = references_from(
            url=page.url,
            wrapping_selector=wrapping_selector,
            local=False,
            remote=True,
            ignore_remotes=ignore_remotes,
        )
        references = list(set(references))  # Remove duplicates
        for ref in references:
            ref_dict = URLDict(
                url=ref,
                clean_url=clean_url(ref),
                harvest_timestamp=datetime.now(),
                source=page.url,
                creation_date=page.creation_date,
                formatted_content=show_page_content(ref, to_string=True),
            )
            if id := add_post(ref_dict):
                ids.append(id)

    return ids


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
) -> list[ObjectId]:
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
) -> list[ObjectId]:
    """Finds and extracts URLs from a given webpage using a CSS selector.

    Note that these pages webpages are collections of blog posts, and that the page
    contents changes as new posts are added. Therefore, we cache the individual post
    pages (we can assume that a blog post is invariant once posted) but we do not cache
    the container pages.

    Args:
        base_url (str): The base URL of the blog or archive page.
        selector (str): The CSS selector to locate article links.
        source (str): A string identifier for the source site.
        date_extractor (Callable[[str], str]): Function to extract a post's date from
                its URL.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids

    Side effects:
       Adds all newly-discovered pages to the MongoDB.
    """
    ids = []

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
        url_dict = URLDict(
            url=absolute_url,
            clean_url=clean_url(absolute_url),
            harvest_timestamp=datetime.now(),
            source=source,
            creation_date=creation_date,
            formatted_content=show_page_content(absolute_url, to_string=True),
        )

        if id := add_post(url_dict):
            ids.append(id)

    return ids


def fetch_multiple_pages(
    urls: list[str],
    scraper_function: Callable[[str], list[ObjectId]],
    max_workers: int = 5,
) -> list[ObjectId]:
    """
    Fetch multiple pages in parallel using ThreadPoolExecutor.

    Args:
        urls (list[str]): List of page URLs to scrape.
        scraper_function (Callable[[str], list[URLDict]]):
            Function that takes a URL and returns a list of new MongoDB doc ids.
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
                logger.error(f"Error fetching {url}: {e}")

    return results


def clean_url(url: str) -> str:
    """
    Remove known tracking parameters (e.g., UTM parameters) from a URL.

    Parameters:
    - url (str): The original URL.

    Returns:
    - str: The cleaned URL without tracking parameters.
    """
    tracking_params = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
    }

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    filtered_params = {
        k: v for k, v in query_params.items() if k not in tracking_params
    }

    cleaned_query = urlencode(filtered_params, doseq=True)
    cleaned_url = urlunparse(parsed_url._replace(query=cleaned_query))

    return cleaned_url
