from typing import Final
from urllib.parse import urljoin

import requests

from blogscraper.ui import console


def normalize_url(base_url: str, link: str) -> str:
    """
    Converts a relative URL to an absolute URL using the base URL.

    Args:
        base_url (str): The base URL of the website.
        link (str): The URL to be normalized.

    Returns:
        str: The normalized absolute URL.
    """
    return urljoin(base_url, link)


def get_html(url: str) -> str | None:
    """
    Wraps fetch_html and returns its result or None on error.
    Prints a brief error messageif the request fails.
    """
    try:
        return fetch_html(url)
    except requests.HTTPError as http_err:
        console.print(
            f"[bold red]HTTP error while fetching {url}: {http_err}[/bold red]"
        )
    except requests.RequestException as req_err:
        console.print(
            f"[bold red]Request error while fetching {url}: {req_err}[/bold red]"
        )
    return None


def fetch_html(url: str) -> str:
    """
    Fetch the raw HTML content from the specified URL with a custom user agent.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The raw HTML content of the page.

    Raises:
        requests.HTTPError: If an HTTP error occurs (e.g. 404, 500).
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
