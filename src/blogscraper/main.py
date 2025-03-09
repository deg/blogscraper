"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

import sys

from blogscraper.tasks import (
    delete_unneeded_docs,
    display_blogs,
    filter_urls_by_date_range,
    generate_doc,
    generate_llm_prompt,
    list_urls,
    scrape_blogs,
)
from blogscraper.ui import confirm_action, console, display_welcome, warnstr
from blogscraper.utils.storage import load_stored_urls


def main() -> None:
    """Starts the Blogscraper CLI and handles user interactions."""
    display_welcome()

    all_urls = []
    if confirm_action("Scrape websites for new URLs?"):
        erase_old = confirm_action("Erase old DB and start fresh?", default=False)
        all_urls = scrape_blogs(erase_old)
    else:
        all_urls = load_stored_urls()

    ranged_urls, start_day, end_day = filter_urls_by_date_range(all_urls)
    if not ranged_urls:
        console.print(warnstr("No posts in the selected time period."))
        return

    if confirm_action("Display contents of selected blogs?"):
        display_blogs(ranged_urls)

    if confirm_action("Display a list of the URLs?"):
        list_urls(ranged_urls)

    if confirm_action("Generate a consolidated Google Doc?"):
        generate_doc(ranged_urls, start_day, end_day)

    if confirm_action("Generate an ad-hoc LLM prompt?"):
        generate_llm_prompt(ranged_urls)

    delete_unneeded_docs()


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user. Exiting...")
        sys.exit(1)
