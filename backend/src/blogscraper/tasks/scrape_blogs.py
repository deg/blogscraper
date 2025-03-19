"""Manages execution of blog-specific scrapers.

This module coordinates the execution of various blog scrapers, deduplicates
newly fetched URLs, and updates stored data.
"""

from typing import Callable

from blogscraper.scrape import SCRAPERS, run_scrapers
from blogscraper.types import URLDict
from blogscraper.ui import select_scrapers
from blogscraper.utils.storage import clear_stored_urls


def scrape_blogs(
    do_all: bool,
    erase_old: bool = False,
    status_callback: Callable[[str], None] | None = None,
) -> list[URLDict]:
    """Handles the website scraping process and returns the scraped URLs."""
    if erase_old:
        clear_stored_urls()

    # [TODO] This is grotesque. We should *not* be passing around a list of strings of
    # numbers. This is only here because of legacy CLI code that should either be
    # replaced or scrapped.
    selected_sites = (
        [str(i) for i in range(len(SCRAPERS))] if do_all else select_scrapers(SCRAPERS)
    )

    results = run_scrapers(selected_sites, SCRAPERS, status_callback=status_callback)
    return results["all_urls"]
