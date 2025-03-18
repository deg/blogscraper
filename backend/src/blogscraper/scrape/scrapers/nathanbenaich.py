from blogscraper.types import Scraper, URLDict

from ..scraper_utils import extend_posts_with_references, fetch_all_urls


def scrape_nathanbenaich(
    scraper: Scraper, existing_urls: list[URLDict]
) -> list[URLDict]:
    """
    Scrapes Nathan Benaich's blog for URLs.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    blogpost_dicts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector="div.portable-archive-list div:has(time)",
        html_a_selector='a[href][data-testid="post-preview-title"]',
        html_time_selector="time[datetime]",
    )

    return extend_posts_with_references(
        blogpost_dicts=blogpost_dicts,
        existing_urls=existing_urls,
        wrapping_selector="article.newsletter-post",
        ignore_remotes=[
            "twitter.com",
            "www.youtube.com",
            "x.com",
        ],
    )
