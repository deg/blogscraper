"""Module for fetching and displaying webpage content.

Uses Trafilatura to extract main content from web pages and formats it
for display in the terminal.

Usage:
    This module provides functions to retrieve and present content from
    specified URLs, either returning it as a string or printing it directly.
"""

import requests
import trafilatura

from blogscraper.ui import console


def show_page_content(url: str, to_string: bool = False) -> str:
    """Fetches, formats, and displays webpage content.

    Args:
        url (str): The URL of the webpage.
        to_string (bool): If True, returns the output as a string instead of printing.

    Returns:
        str: The formatted content if `to_string` is True, otherwise an empty string.
    """
    content = fetch_page_content(url)
    formatted_content = format_page_content(url, content)

    if to_string:
        return formatted_content
    else:
        console.print(formatted_content)
        return ""


def fetch_page_content(url: str) -> str | None:
    """Fetches and extracts the main content of a webpage as Markdown.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str | None: Extracted content as Markdown, or None if extraction fails.
    """
    try:
        # Use trafilatura to extract the main content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None

        main_content = trafilatura.extract(
            downloaded,
            favor_recall=True,
            include_formatting=True,
            include_images=True,
            include_links=True,
            include_tables=True,
            output_format="markdown",
            with_metadata=True,
            date_extraction_params={
                "max_date": "2029-12-31",
                "outputformat": "%Y-%m-%d %H:%M %z",
            },
        )
        return main_content if main_content else None

    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")
        return None


def format_page_content(url: str, content: str | None) -> str:
    """Formats the extracted content into a structured string for display.

    Args:
        url (str): The URL of the webpage.
        content (str | None): The extracted content.

    Returns:
        str: Formatted content string.
    """
    if not content:
        return f"No main content found for {url}."

    headers, body = split_headers_body(content)
    formatted_output = "\n".join(
        [
            f"\n\f<!-- START OF POST FROM {url} -->",
            "\n<!-- PAGE HEADERS -->\n",
            f"{headers}",
            "\n<!-- CONTENT -->\n",
            f"{body}",
            "\n<!-- END OF POST -->\n",
        ]
    )
    return formatted_output


def split_headers_body(text: str) -> tuple[str, str]:
    """Splits the given text into a YAML-like header and the body.

    Args:
        text (str): The input text containing a header and body.

    Returns:
        tuple[str, str]: A tuple with (header, body).
    """
    parts = text.split("---", 2)  # Split at the first two '---' occurrences
    if len(parts) < 3:
        return "", text.strip()  # If no valid header found, return full text as body
    return parts[1].strip(), parts[2].strip()
