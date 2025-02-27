from blogscraper.types import URLDict


def main() -> None:
    # Call run_scrapers with test_mode set to False
    run_scrapers(test_mode=False)


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
