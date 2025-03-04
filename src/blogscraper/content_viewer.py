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
                console.print(Panel(main_content, title=f"Content of {url}"))
            else:
                console.print(f"[yellow]No main content found for {url}.[/yellow]")
        else:
            console.print(f"[red]Failed to download content from {url}.[/red]")
    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")
