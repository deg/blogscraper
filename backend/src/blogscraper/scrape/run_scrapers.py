from typing import Callable

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.mongodb_helpers import PostCollection
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)


def run_scrapers(
    posts_coll: PostCollection,
    selected_sites: list[str],
    scrapers: list[Scraper],
    status_callback: Callable[[str], None] | None = None,
) -> dict[str, list[URLDict]]:
    """Scrapes blog entries from selected sites and updates stored URLs.

    Args:
        selected_sites (list[str]): List of selected scraper names.
        scrapers (list[Scraper]): List of scraper objects.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    print(f"TEMP: {posts_coll}")
    existing_urls = load_stored_urls()

    all_new_urls = []
    for index, scraper in enumerate(scrapers):
        if status_callback:
            status_callback(f"Scraping {index}: {scraper.name}")
        if str(index) in selected_sites:
            all_new_urls.extend(scraper.function(scraper, existing_urls))

    if status_callback:
        status_callback("deduplicating and saving")
    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)

    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
        "all_urls": existing_urls + unique_new_urls,
    }
