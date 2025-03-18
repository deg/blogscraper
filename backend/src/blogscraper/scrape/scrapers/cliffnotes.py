from blogscraper.types import Scraper, URLDict

from ..scraper_utils import extend_posts_with_references, fetch_all_urls


def scrape_cliffnotes(scraper: Scraper, existing_urls: list[URLDict]) -> list[URLDict]:
    """
    Scrapes Cliffnotes's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    blogpost_dicts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector='a[href^="/p/"]:has(time)',
        html_time_selector="time[datetime]",
    )

    return extend_posts_with_references(
        blogpost_dicts=blogpost_dicts,
        existing_urls=existing_urls,
        wrapping_selector="div.rendered-post",
        ignore_remotes=[
            "courses.cliffnotes.ai",
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
    )
