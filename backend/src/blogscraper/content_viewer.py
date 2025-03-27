"""Module for fetching and displaying webpage content.

Uses Trafilatura to extract main content from web pages and formats it
for display in the terminal.

Usage:
    This module provides functions to retrieve content from specified
    URLs and format it readably.
"""

import asyncio

import requests
import trafilatura
from degel_python_utils import setup_logger
from playwright.async_api import async_playwright

logger = setup_logger(__name__)


def formatted_page_content(url: str) -> str:
    """Returns formmated content of a web page.

    Args:
        url (str): The URL of the webpage.

    Returns:
        str: The formatted content.
    """
    content = fetch_page_content(url)
    formatted_content = format_page_content(url, content)
    return formatted_content


def fetch_page_content(url: str) -> str | None:
    """Fetches and extracts the main content of a webpage as Markdown.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str | None: Extracted content as Markdown, or None if extraction fails.
    """
    try:
        # Fetch the page HTML
        downloaded = trafilatura.fetch_url(url)
        main_content = extract_content(downloaded) if downloaded else None

        if main_content:
            return main_content

        logger.minor(f"🌀 Falling back to Playwright for {url}")
        return asyncio.run(fetch_rendered_and_extract(url))

    except requests.RequestException as e:
        logger.warning(f"🔥 Failed to fetch {url!r}: {e}")
        return None


async def fetch_rendered_and_extract(url: str) -> str | None:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=10000
                )
                if response and "text/html" not in response.headers.get(
                    "content-type", ""
                ):
                    logger.warning(
                        f"💥 Non-HTML content at {url!r}: "
                        f"{response.headers.get('content-type')}"
                    )
                    return None
                html = await page.content()
                return extract_content(html)
            finally:
                await browser.close()
    except Exception as e:
        logger.warning(f"🔥 Playwright failed to fetch {url!r}: {e}")
        return None


def extract_content(html: str) -> str | None:
    return trafilatura.extract(
        html,
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
