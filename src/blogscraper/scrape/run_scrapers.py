from blogscraper.types import Scraper, URLDict
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)


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
            all_new_urls.extend(scraper.function(scraper))

    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)

    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
        "all_urls": existing_urls + unique_new_urls,
    }
