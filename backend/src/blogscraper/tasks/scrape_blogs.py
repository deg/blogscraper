"""Manages execution of blog-specific scrapers.

This module coordinates the execution of various blog scrapers, deduplicates
newly fetched URLs, and updates stored data.
"""

from typing import Callable

from bson import ObjectId
from degel_python_utils import setup_logger

from blogscraper.scrape import SCRAPERS, run_scrapers

logger = setup_logger(__name__)


def scrape_blogs(
    # - do_all: bool = False,
    status_callback: Callable[[str], None] | None = None,
) -> list[ObjectId]:
    """Handles the website scraping process and returns the scraped URLs."""

    # [TODO] This is grotesque. We should *not* be passing around a list of strings of
    # numbers. This is only here because of legacy CLI code that should either be
    # replaced or scrapped.
    logger.warning("Still supporting only do_all. Fix scrape_blogs soon")
    selected_sites = [
        str(i) for i in range(len(SCRAPERS))
    ]  # - if do_all else select_scrapers(SCRAPERS)

    return run_scrapers(
        selected_sites=selected_sites,
        scrapers=SCRAPERS,
        status_callback=status_callback,
    )
