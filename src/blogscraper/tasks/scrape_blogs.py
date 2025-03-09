"""Manages execution of blog-specific scrapers.

This module coordinates the execution of various blog scrapers, deduplicates
newly fetched URLs, and updates stored data.
"""

from blogscraper.scrape import SCRAPERS, run_scrapers
from blogscraper.types import URLDict
from blogscraper.ui import select_scrapers
from blogscraper.utils.storage import clear_stored_urls


def scrape_blogs(erase_old: bool) -> list[URLDict]:
    """Handles the website scraping process and returns the scraped URLs."""
    if erase_old:
        clear_stored_urls()

    selected_sites = select_scrapers(SCRAPERS)

    results = run_scrapers(selected_sites, SCRAPERS)
    return results["all_urls"]
