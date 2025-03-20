from typing import Callable

from bson import ObjectId

from blogscraper.types import Scraper

from ..scraper_utils import standard_scraper


def scrape_cliffnotes(
    scraper: Scraper, status_callback: Callable[[str], None] | None = None
) -> list[ObjectId]:
    """
    Scrapes Cliffnotes's blog for URLs.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids
    """
    return standard_scraper(
        scraper=scraper,
        section_selector='a[href^="/p/"]:has(time)',
        wrapping_selector="div.rendered-post",
        html_time_selector="time[datetime]",
        ignore_remotes=[
            "courses.cliffnotes.ai",
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
        status_callback=status_callback,
    )
