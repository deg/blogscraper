import requests
import trafilatura
from rich.panel import Panel

from blogscraper.ui import console


def show_page_content(url: str) -> None:
    """
    Fetch and display the main content of a webpage as Markdown.

    Args:
        url (str): The URL of the webpage to fetch.
    """
    try:
        # Use trafilatura to extract the main content
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
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
                    "outputformat": "%Y-%m-%dT%H:%M:%S%z",
                },
            )
            if main_content:
                headers, body = split_headers_body(main_content)
                console.print(Panel("Page headers"))
                console.print(f"[grey19]{headers}[/grey19]")
                console.print(Panel("Content"))
                console.print(f"[grey19]{body}[/grey19]")
                console.print(Panel("End of page"))
            else:
                console.print(f"[yellow]No main content found for {url}.[/yellow]")
        else:
            console.print(f"[red]Failed to download content from {url}.[/red]")
    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")


def split_headers_body(text: str) -> tuple[str, str]:
    """
    Splits the given text into a YAML-like header and the body.

    Args:
        text (str): The input text containing a header and body.

    Returns:
        tuple[str, str]: A tuple with (header, body).
    """
    parts = text.split("---", 2)  # Split at the first two '---' occurrences
    if len(parts) < 3:
        return "", text.strip()  # If no valid header found, return full text as body
    return parts[1].strip(), parts[2].strip()
