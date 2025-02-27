import argparse

from blogscraper.types import URLDict


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
        list[URLDict]: A placeholder list of URLs.
    """
    if test_mode:
        print("Running scrapers in test mode")
    else:
        print("Running scrapers in normal mode")

    # Placeholder for the list of URLs
    return []


if __name__ == "__main__":  # pragma: no cover
    main()
