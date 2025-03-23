"""Utility functions for handling and fetching URLs.

Provides functions to normalize URLs, fetch HTML content, and handle HTTP errors
in a structured way.

Usage:
    These functions assist scrapers by ensuring reliable URL resolution and
    content retrieval.
"""

from typing import Final
from urllib.parse import urljoin

import requests
from degel_python_utils import setup_logger

logger = setup_logger(__name__)


def normalize_url(base_url: str, link: str) -> str:
    """Converts a relative URL to an absolute URL using the given base URL.

    Args:
        base_url (str): The base URL of the website.
        link (str): The URL to be normalized.

    Returns:
        str: The absolute URL.
    """
    return urljoin(base_url, link)


def get_html(url: str) -> str | None:
    """Fetches HTML content from the given URL, handling request errors gracefully.

    Args:
        url (str): The URL to fetch.

    Returns:
        str | None: The HTML content if the request succeeds, otherwise None.
    """
    try:
        return fetch_html(url)
    except requests.HTTPError as http_err:
        logger.warning(f"HTTP error while fetching {url}: {http_err}")
    except requests.RequestException as req_err:
        logger.warning(f"Request error while fetching {url}: {req_err}")
    return None


def fetch_html(url: str) -> str:
    """Fetches the raw HTML content from the specified URL with a custom user agent.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The raw HTML content of the page.

    Raises:
        requests.HTTPError: If an HTTP error occurs (e.g., 404, 500).
    """
    USER_AGENT: Final[str] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )
    headers: dict[str, str] = {"User-Agent": USER_AGENT}

    response: requests.Response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text
