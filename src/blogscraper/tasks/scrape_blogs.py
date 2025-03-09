"""Manages execution of blog-specific scrapers.

This module coordinates the execution of various blog scrapers, deduplicates
newly fetched URLs, and updates stored data.
"""

from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import Scraper, URLDict
from blogscraper.ui import select_scrapers
from blogscraper.utils.storage import (
    clear_stored_urls,
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)

SCRAPERS = [
    Scraper(name="The Zvi", function=scrape_thezvi),
    Scraper(name="Simon Willison", function=scrape_simonwillison),
    Scraper(name="Nathan Benaich", function=scrape_nathanbenaich),
    Scraper(name="Cliffnotes", function=scrape_cliffnotes),
]


def scrape_blogs(erase_old: bool) -> list[URLDict]:
    """Handles the website scraping process and returns the scraped URLs."""
    if erase_old:
        clear_stored_urls()

    selected_sites = select_scrapers(SCRAPERS)
    results = run_scrapers(selected_sites, SCRAPERS)
    return results["all_urls"]


def run_scrapers(
    selected_sites: list[str], scrapers: list[Scraper]
) -> dict[str, list[URLDict]]:
    """Scrapes blog entries from selected sites and updates stored URLs.

    Args:
        selected_sites (list[str]): List of selected scraper names.
        scrapers (list[Scraper]): List of scraper objects.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    existing_urls = load_stored_urls()

    all_new_urls = []
    for index, scraper in enumerate(scrapers):
        if str(index) in selected_sites:
            all_new_urls.extend(scraper.function())

    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)

    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
        "all_urls": existing_urls + unique_new_urls,
    }
