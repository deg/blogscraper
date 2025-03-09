"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse

from blogscraper.content_viewer import show_page_content
from blogscraper.prompt import PROMPT_PREFIX, PROMPT_SUFFIX
from blogscraper.scraper_manager import run_scrapers
from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import GDoc, Scraper, URLDict
from blogscraper.ui import (
    confirm_action,
    console,
    display_welcome,
    infostr,
    input_date,
    select_google_docs,
    select_scrapers,
    select_urls,
    warnstr,
)
from blogscraper.utils.google_interface import (
    create_google_doc,
    delete_service_account_doc,
    list_service_account_docs,
    write_to_google_doc,
)
from blogscraper.utils.storage import clear_stored_urls, load_stored_urls
from blogscraper.utils.time_utils import datestring

SCRAPERS = [
    Scraper(name="The Zvi", function=scrape_thezvi),
    Scraper(name="Simon Willison", function=scrape_simonwillison),
    Scraper(name="Nathan Benaich", function=scrape_nathanbenaich),
    Scraper(name="Cliffnotes", function=scrape_cliffnotes),
]


def main() -> None:
    """Starts the Blogscraper CLI and handles user interactions."""
    display_welcome()

    all_urls = []
    if confirm_action("Scrape websites for new URLs?"):
        erase_old = confirm_action("Erase old DB and start fresh?", default=False)
        all_urls = handle_scraping(erase_old)
    else:
        all_urls = load_stored_urls()

    ranged_urls, start_day, end_day = filter_urls_by_date_range(all_urls)
    if not ranged_urls:
        console.print(warnstr("No posts in the selected time period."))
        return

    if confirm_action("Display contents of selected blogs?"):
        handle_content_display(ranged_urls)

    if confirm_action("Display a list of the URLs?"):
        handle_url_list(ranged_urls)

    if confirm_action("Generate a consolidated Google Doc?"):
        handle_google_doc_generation(ranged_urls, start_day, end_day)

    if confirm_action("Generate an ad-hoc LLM prompt?"):
        handle_llm_prompt_generation(ranged_urls)

    all_old_google_docs = list_service_account_docs()
    if all_old_google_docs and confirm_action("Delete some old Google Docs?"):
        handle_google_doc_cleanup(all_old_google_docs)


def handle_scraping(erase_old: bool) -> list[URLDict]:
    """Handles the website scraping process and returns the scraped URLs."""
    if erase_old:
        clear_stored_urls()

    selected_sites = select_scrapers(SCRAPERS)
    results = run_scrapers(selected_sites, SCRAPERS)
    return results["all_urls"]


def filter_urls_by_date_range(
    all_urls: list[URLDict],
) -> tuple[list[URLDict], datetime, datetime]:
    """Filters scraped URLs based on user-defined date range."""
    today = datetime.today()
    last_week = today - timedelta(days=7)

    start_day = input_date("First day to analyze", last_week)
    end_day = input_date("Last day to analyze", today)

    return get_range_of_urls(all_urls, start_day, end_day), start_day, end_day


def handle_content_display(ranged_urls: list[URLDict]) -> None:
    """Displays blog contents for selected URLs."""
    for url_dict in ranged_urls:
        if confirm_action(f"See content of {url_dict['url']}?"):
            show_page_content(url_dict["url"], to_string=False)


def handle_url_list(ranged_urls: list[URLDict]) -> None:
    """Displays a list of URLs."""
    for url_dict in ranged_urls:
        console.print(f"[blue3]{url_dict['url']}[/blue3]")


def handle_google_doc_generation(
    ranged_urls: list[URLDict], start_day: datetime, end_day: datetime
) -> None:
    """Generates a Google Document with selected blog content."""
    selected_urls = select_urls(ranged_urls)
    document_content = prepare_google_doc_content(selected_urls)

    human_start = datestring(start_day, human=True)
    human_end = datestring(end_day, human=True)

    doc_id, doc_url = create_google_doc(f"{human_start} - {human_end} blog scrape")
    write_to_google_doc(doc_id, document_content)
    console.print(infostr(f"Created Google doc: {doc_url}"))


def prepare_google_doc_content(selected_urls: list[str]) -> str:
    """Prepares the content for the Google Document."""
    text = "<!-- This document is a set of blog posts focused on AI innovations -->\n\n"
    text += "<!-- TABLE OF CONTENTS -->\n\n"
    text += "\n".join(selected_urls) + "\n\n"

    for i, url in enumerate(selected_urls, start=1):
        contents = show_page_content(url, to_string=True)
        text += contents
        console.print(
            infostr(f"Adding {i}/{len(selected_urls)} (len={len(contents)}): {url}")
        )

        if (len_so_far := len(text)) > 1_000_000:
            console.print(
                warnstr(
                    f"This document is getting long ({len_so_far}. "
                    + "It may be too big for Google Docs).\n"
                    + "Not appendng more documents.\n"
                    + "Table of contents will be inconsistent."
                )
            )
            break

    return text


def handle_llm_prompt_generation(ranged_urls: list[URLDict]) -> None:
    """Generates an LLM prompt based on the scraped data."""
    console.print(
        f"[grey19]{PROMPT_PREFIX}\n\n"
        + f"{generate_title_list(ranged_urls)}\n\n"
        + f"{PROMPT_SUFFIX}[/grey19]"
    )


def handle_google_doc_cleanup(old_docs: list[GDoc]) -> None:
    """Deletes selected old Google Docs."""
    doc_ids_to_delete = select_google_docs(old_docs, "delete")
    for doc in doc_ids_to_delete:
        delete_service_account_doc(doc.id, doc.name)


def get_range_of_urls(
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

    ranged_urls = [
        url_dict
        for url_dict in urls
        if first_date <= datetime.fromisoformat(url_dict["creation_date"]) <= last_date
    ]

    # Sort the URLs by creation_date, earliest first
    ranged_urls.sort(key=lambda x: datetime.fromisoformat(x["creation_date"]))
    return ranged_urls


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
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user. Exiting...")
        sys.exit(1)
