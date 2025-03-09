from datetime import datetime, timedelta

from blogscraper.types import URLDict
from blogscraper.ui import input_date


def filter_urls_by_date_range(
    all_urls: list[URLDict],
) -> tuple[list[URLDict], datetime, datetime]:
    """Filters scraped URLs based on user-defined date range."""
    today = datetime.today()
    last_week = today - timedelta(days=7)

    start_day = input_date("First day to analyze", last_week)
    end_day = input_date("Last day to analyze", today)

    return get_range_of_urls(all_urls, start_day, end_day), start_day, end_day


def get_range_of_urls(
    urls: list[URLDict], first_date: datetime, last_date: datetime
) -> list[URLDict]:
    """Filters URLs collected within the specified date range (inclusive).

    Args:
        urls (list[URLDict]): List of existing URL dicts.
        first_date (datetime): The start of the date range (inclusive).
        last_date (datetime): The end of the date range (inclusive).

    Returns:
        list[URLDict]: A list of URLs within the date range.
    """
    first_date = first_date.replace(hour=0, minute=0, second=0)
    last_date = last_date.replace(hour=23, minute=59, second=59)

    ranged_urls = [
        url_dict
        for url_dict in urls
        if first_date <= datetime.fromisoformat(url_dict["creation_date"]) <= last_date
    ]

    # Sort the URLs by creation_date, earliest first
    ranged_urls.sort(key=lambda x: datetime.fromisoformat(x["creation_date"]))
    return ranged_urls
