from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from blogscraper.content_viewer import show_page_content
from blogscraper.prompt import PROMPT_PREFIX, PROMPT_SUFFIX
from blogscraper.scraper_manager import run_scrapers
from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import Scraper, URLDict
from blogscraper.ui import (
    confirm_action,
    display_welcome,
    input_lookback_days,
    select_scrapers,
)
from blogscraper.utils.storage import clear_stored_urls, load_stored_urls

SCRAPERS = [
    Scraper(name="The Zvi", function=scrape_thezvi),
    Scraper(name="Simon Willison", function=scrape_simonwillison),
    Scraper(name="Nathan Benaich", function=scrape_nathanbenaich),
    Scraper(name="Cliffnotes", function=scrape_cliffnotes),
]


def main() -> None:
    display_welcome()

    scrape = confirm_action("Do you want to scrape new URLs?")
    if scrape:
        delete_old = confirm_action("Erase old DB and start fresh?", default=False)
        if delete_old:
            clear_stored_urls()
        selected_sites = select_scrapers(SCRAPERS)
        results = run_scrapers(selected_sites, SCRAPERS)
    else:
        results = {"existing_urls": load_stored_urls()}

    view_contents = confirm_action("Do you want to see the page contents?")
    generate_prompt = confirm_action("Do you want to generate an LLM prompt?")

    if not view_contents and not generate_prompt:
        return

    lookback_days = input_lookback_days()
    relevant = recent_urls(results["existing_urls"], lookback_days)

    if view_contents:
        for url_dict in relevant:
            if confirm_action(f"Do you want to see the content for {url_dict['url']}?"):
                show_page_content(url_dict["url"])

    if generate_prompt:
        print(f"{PROMPT_PREFIX}\n\n{generate_title_list(relevant)}\n\n{PROMPT_SUFFIX}")


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


def generate_title_list(urls: list[URLDict]) -> str:
    """
    Return a numbered list of titles and URLs, e.g.,
    1. "Economics Roundup 5" -
       https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    2. ...
    """
    lines = []
    for i, url_dict in enumerate(urls, start=1):
        formatted = url_to_title_string(url_dict["url"])
        lines.append(f"{i}. {formatted}")
    return "\n".join(lines)


def url_to_title_string(url: str) -> str:
    """
    Convert a URL like
        https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    into a string like
        "Economics Roundup 5" -
         https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    """
    parsed = urlparse(url)
    path_segments = [seg for seg in parsed.path.split("/") if seg]
    if not path_segments:
        # If there's no last segment, just return the URL as-is
        return f'"{url}" - {url}'

    # The last segment might be "economics-roundup-5"
    last_segment = path_segments[-1]
    # Replace hyphens with spaces and title-case it
    title = last_segment.replace("-", " ").title()
    return f'"{title}" - {url}'


if __name__ == "__main__":  # pragma: no cover
    main()
