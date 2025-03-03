import argparse
from datetime import datetime, timedelta, timezone

from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import URLDict
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)


def main() -> None:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the blog scrapers.")
    parser.add_argument(
        "--lookback",
        type=int,
        help="Print URLs collected within the last N days",
    )
    parser.add_argument(
        "--scrape",
        action="store_true",
        default=True,
        help="Run scrapers to collect new URLs (default: True)",
    )
    parser.add_argument(
        "--no-scrape",
        dest="scrape",
        action="store_false",
        help="Do not run scrapers to collect new URLs",
    )
    args = parser.parse_args()

    # Run scrapers and process URLs if --scrape is true
    if args.scrape:
        results = run_scrapers()
    else:
        results = {"existing_urls": load_stored_urls()}

    # Handle the --lookback flag
    if args.lookback is not None:
        relevant = recent_urls(results["existing_urls"], args.lookback)
        print(f"URLs collected in the last {args.lookback} days:")
        for url_dict in relevant:
            print(url_dict["url"])


def recent_urls(urls: list[URLDict], lookback_days: int) -> list[URLDict]:
    """
    Prints URLs that were collected within the last 'lookback_days' days.

    Args:
        existing_urls (list[URLDict]): List of existing URLs.
        lookback_days (int): Number of days to look back.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent_urls = [
        url_dict
        for url_dict in urls
        if datetime.fromisoformat(url_dict["creation_date"]) > cutoff_date
    ]

    # Sort the URLs by creation_date, earliest first
    recent_urls.sort(key=lambda x: datetime.fromisoformat(x["creation_date"]))
    return recent_urls


def run_scrapers() -> dict[str, list[URLDict]]:
    """
    Scrape blog entries from interesting sites.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    # Load existing URLs from urls.json
    existing_urls = load_stored_urls()

    # Scrape new URLs from different sources
    new_urls_thezvi = scrape_thezvi()
    new_urls_simonwillison = scrape_simonwillison()

    # Combine all new URLs
    all_new_urls = new_urls_thezvi + new_urls_simonwillison

    # Deduplicate and save new URLs
    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)
    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
    }


if __name__ == "__main__":  # pragma: no cover
    main()
