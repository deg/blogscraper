"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

from datetime import datetime, timedelta
from urllib.parse import urlparse

from blogscraper.content_viewer import show_page_content
from blogscraper.prompt import PROMPT_PREFIX, PROMPT_SUFFIX
from blogscraper.scraper_manager import run_scrapers
from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import Scraper, URLDict
from blogscraper.ui import (
    confirm_action,
    console,
    display_welcome,
    input_date,
    select_scrapers,
    select_urls,
)
from blogscraper.utils.google_interface import create_google_doc, write_to_google_doc
from blogscraper.utils.storage import clear_stored_urls, load_stored_urls

SCRAPERS = [
    Scraper(name="The Zvi", function=scrape_thezvi),
    Scraper(name="Simon Willison", function=scrape_simonwillison),
    Scraper(name="Nathan Benaich", function=scrape_nathanbenaich),
    Scraper(name="Cliffnotes", function=scrape_cliffnotes),
]


def main() -> None:
    """Starts the Blogscraper CLI and handles user interactions."""
    display_welcome()

    scrape = confirm_action("Do you want to scrape new URLs?")
    if scrape:
        delete_old = confirm_action("Erase old DB and start fresh?", default=False)
        if delete_old:
            clear_stored_urls()
        # [TODO] Fix select_scrapers to be like select_urls,
        #        rather than using enumerate
        selected_sites = select_scrapers(SCRAPERS)
        results = run_scrapers(selected_sites, SCRAPERS)
        all_urls = results["all_urls"]
    else:
        all_urls = load_stored_urls()

    today = datetime.today()
    last_week = today - timedelta(days=7)
    start_day = input_date("First day to collect", last_week)
    end_day = input_date("Last day to collect", today)
    recent = recent_urls(all_urls, start_day, end_day)

    if not recent:
        console.print("[red]No posts in the selected time period.[/red]")
        return

    view_contents = confirm_action(
        "Do you want to see the page contents of recent blogs?"
    )
    if view_contents:
        for url_dict in recent:
            if confirm_action(f"Do you want to see the content for {url_dict['url']}?"):
                show_page_content(url_dict["url"], to_string=False)

    generate_list = confirm_action("Do you want a list of the URLs?")
    if generate_list:
        for url_dict in recent:
            console.print(f"[blue3]{url_dict['url']}[/blue3]")

    generate_doc = confirm_action("Do you want to generate a consolidated document?")
    if generate_doc:
        selected_urls = select_urls(recent)
        text = (
            "<!-- This document is a set of very recent"
            + "blog posts focused on AI innovations -->\n\n"
            + "<!-- TABLE OF CONTENTS -->\n\n"
        )
        for url in selected_urls:
            text += f"{url}\n"
        text += "\n\n"

        for url in selected_urls:
            text += show_page_content(url, to_string=True)

        doc_id, doc_url = create_google_doc(f"BlogScraper document of {datetime.now()}")
        write_to_google_doc(doc_id, text)
        console.print(f"[red]Created Google doc: {doc_url}[/red]")

    generate_prompt = confirm_action("Do you want to generate an LLM prompt?")
    if generate_prompt:
        console.print(
            f"[grey19]{PROMPT_PREFIX}\n\n"
            + f"{generate_title_list(recent)}\n\n"
            + f"{PROMPT_SUFFIX}[/grey19]"
        )


def recent_urls(
    urls: list[URLDict], first_date: datetime, last_date: datetime
) -> list[URLDict]:
    """Filters URLs collected within the specified date range (inclusive).

    Args:
        urls (list[URLDict]): List of existing URL dicts.
        first_date (datetime): The start of the date range (inclusive).
        last_date (datetime): The end of the date range (inclusive).

    Returns:
        list[URLDict]: A list of URLs within the date range.
    """
    first_date = first_date.replace(hour=0, minute=0, second=0)
    last_date = last_date.replace(hour=23, minute=59, second=59)

    recent = [
        url_dict
        for url_dict in urls
        if first_date <= datetime.fromisoformat(url_dict["creation_date"]) <= last_date
    ]

    # Sort the URLs by creation_date, earliest first
    recent.sort(key=lambda x: datetime.fromisoformat(x["creation_date"]))
    return recent


def generate_title_list(urls: list[URLDict]) -> str:
    """Returns a numbered list of titles and URLs, e.g.,
    1. "Economics Roundup 5" -
       https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    2. ...

    Args:
        urls (list[URLDict]): A list of URLDict objects containing URLs and metadata.

    Returns:
        str: A formatted string listing numbered titles and URLs.
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

    Args:
        url (str): The URL to extract a title from.

    Returns:
        str: A formatted title extracted from the URL.
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
