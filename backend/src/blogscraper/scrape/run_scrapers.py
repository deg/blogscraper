from typing import Callable

from bson import ObjectId
from degel_python_utils import setup_logger

from blogscraper.types import Scraper

logger = setup_logger(__name__)


def run_scrapers(
    selected_sites: list[str],
    scrapers: list[Scraper],
    status_callback: Callable[[str], None] | None = None,
) -> list[ObjectId]:
    """Scrapes blog entries from selected sites and updates stored URLs.

    Args:
        selected_sites (list[str]): List of selected scraper names.
        scrapers (list[Scraper]): List of scraper objects.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    all_new_docs = []
    for index, scraper in enumerate(scrapers):
        if status_callback:
            status_callback(f"Scraping {index}: {scraper.name}")
        if str(index) in selected_sites:
            all_new_docs.extend(scraper.function(scraper, status_callback))

    if status_callback:
        status_callback("Done")

    return all_new_docs
