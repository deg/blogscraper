from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import questionary
import requests
from bs4 import BeautifulSoup
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.prompt import PROMPT_PREFIX, PROMPT_SUFFIX
from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import URLDict
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)

console = Console()


def main() -> None:
    console.print(Panel("Welcome to the Blog Scraper!", title="Blog Scraper"))

    # Ask the user if they want to scrape new URLs
    scrape = questionary.confirm("Do you want to scrape new URLs?").ask()

    if scrape:
        # Display choices for which sites to scrape, defaulting to all selected
        selected_sites = questionary.checkbox(
            "Select sites to scrape:",
            choices=[
                Choice("The Zvi", value="1", checked=True),
                Choice("Simon Willison", value="2", checked=True),
                Choice("Nathan Benaich", value="3", checked=True),
                Choice("Cliffnotes", value="4", checked=True),
            ],
        ).ask()

        results = run_scrapers(selected_sites)
    else:
        results = {"existing_urls": load_stored_urls()}

    # Ask if the user wants to see the page contents
    view_contents = questionary.confirm("Do you want to see the page contents?").ask()

    # Ask if the user wants to generate an LLM prompt
    generate_prompt = questionary.confirm(
        "Do you want to generate an LLM prompt?"
    ).ask()

    if not view_contents and not generate_prompt:
        return

    while True:
        try:
            lookback_days = int(
                questionary.text("Enter the number of days to look back:").ask()
            )
            break
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")

    relevant = recent_urls(results["existing_urls"], lookback_days)

    if view_contents:
        for url_dict in relevant:
            view_page = questionary.confirm(
                f"Do you want to see the content for {url_dict['url']}?"
            ).ask()
            if view_page:
                show_page_content(url_dict["url"])

    if generate_prompt:
        # Ask for lookback days with validation

        print(f"{PROMPT_PREFIX}\n\n{generate_title_list(relevant)}\n\n{PROMPT_SUFFIX}")


def show_page_content(url: str) -> None:
    """
    Fetch and display the content of a webpage.

    Args:
        url (str): The URL of the webpage to fetch.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        console.print(Panel(text, title=f"Content of {url}"))
    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")


def run_scrapers(selected_sites: list[str]) -> dict[str, list[URLDict]]:
    """
    Scrape blog entries from selected sites.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    existing_urls = load_stored_urls()

    # Scrape new URLs from selected sources
    all_new_urls = []
    if "1" in selected_sites:
        all_new_urls.extend(scrape_thezvi())
    if "2" in selected_sites:
        all_new_urls.extend(scrape_simonwillison())
    if "3" in selected_sites:
        all_new_urls.extend(scrape_nathanbenaich())
    if "4" in selected_sites:
        all_new_urls.extend(scrape_cliffnotes())

    # Deduplicate and save new URLs
    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)
    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
    }


def recent_urls(urls: list[URLDict], lookback_days: int) -> list[URLDict]:
    """
    Prints URLs that were collected within the last 'lookback_days' days.

    Args:
        existing_urls (list[URLDict]): List of existing URLs.
        lookback_days (int): Number of days to look back.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent_urls = [
        url_dict
        for url_dict in urls
        if datetime.fromisoformat(url_dict["creation_date"]) > cutoff_date
    ]

    # Sort the URLs by creation_date, earliest first
    recent_urls.sort(key=lambda x: datetime.fromisoformat(x["creation_date"]))
    return recent_urls


def generate_title_list(urls: list[URLDict]) -> str:
    """
    Return a numbered list of titles and URLs, e.g.,
    1. "Economics Roundup 5" -
       https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    2. ...
    """
    lines = []
    for i, url_dict in enumerate(urls, start=1):
        formatted = url_to_title_string(url_dict["url"])
        lines.append(f"{i}. {formatted}")
    return "\n".join(lines)


def url_to_title_string(url: str) -> str:
    """
    Convert a URL like
        https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    into a string like
        "Economics Roundup 5" -
         https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    """
    parsed = urlparse(url)
    path_segments = [seg for seg in parsed.path.split("/") if seg]
    if not path_segments:
        # If there's no last segment, just return the URL as-is
        return f'"{url}" - {url}'

    # The last segment might be "economics-roundup-5"
    last_segment = path_segments[-1]
    # Replace hyphens with spaces and title-case it
    title = last_segment.replace("-", " ").title()
    return f'"{title}" - {url}'


if __name__ == "__main__":  # pragma: no cover
    main()
