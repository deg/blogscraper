import argparse

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
        "--test",
        action="store_true",
        help="Run scrapers in test mode",
    )
    args = parser.parse_args()

    # Determine the mode based on the --test flag
    test_mode = args.test

    # Call run_scrapers with the determined test_mode
    urls = run_scrapers(test_mode=test_mode)

    # If in test mode, print the returned URLs
    if test_mode:
        print("Test mode URLs:", urls)


def run_scrapers(test_mode: bool) -> list[URLDict]:
    """
    Runs the scrapers in either test or normal mode.

    Args:
        test_mode (bool): If True, runs in test mode; otherwise, runs in normal mode.

    Returns:
        list[URLDict]: A list of new URLs.
    """
    # Load existing URLs from urls.json
    existing_urls = load_stored_urls()

    # Scrape new URLs from different sources
    new_urls_thezvi = scrape_thezvi()
    new_urls_simonwillison = scrape_simonwillison()

    # Combine all new URLs
    all_new_urls = new_urls_thezvi + new_urls_simonwillison

    if test_mode:
        print("Running scrapers in test mode")
        # Print the new URLs instead of saving them
        print("New URLs:", all_new_urls)
    else:
        print("Running scrapers in normal mode")
        # Deduplicate and save new URLs
        unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
        save_stored_urls(existing_urls + unique_new_urls)

    return all_new_urls


if __name__ == "__main__":  # pragma: no cover
    main()
