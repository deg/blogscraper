from typing import Callable

from bson import ObjectId

from blogscraper.types import Scraper

from ..scraper_utils import standard_scraper


def scrape_nathanbenaich(
    scraper: Scraper, status_callback: Callable[[str], None] | None = None
) -> list[ObjectId]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[ObjectId]: Newly added MongoDB document ids
    """
    return standard_scraper(
        scraper=scraper,
        section_selector="div.portable-archive-list div:has(time)",
        html_a_selector='a[href][data-testid="post-preview-title"]',
        html_time_selector="time[datetime]",
        wrapping_selector="article.newsletter-post",
        ignore_remotes=[
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
        status_callback=status_callback,
    )
