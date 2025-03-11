import re
from datetime import datetime

from blogscraper.types import Scraper, URLDict
from blogscraper.utils.time_utils import datestring

from ..scraper_utils import fetch_all_urls, references_from

# Define a constant for the number of threads
MAX_WORKERS = 5


def scrape_thezvi(scraper: Scraper) -> list[URLDict]:
    """
    Scrapes The Zvi's blog for URLs, including archived old posts.

    Returns:
        list[URLDict]: A list of URLDict objects.
    """
    blogpost_dicts = fetch_all_urls(
        base_url=scraper.base_url,
        source_name=scraper.name,
        selector="h2.entry-title a",
        archive_selector="li#archives-2 a",
        url_date_parser=extract_thezvi_date,
    )

    ref_dicts: list[URLDict] = []
    for page in blogpost_dicts:
        references = references_from(
            url=page["url"],
            wrapping_selector="div#content",
            local=False,
            remote=True,
            ignore_remotes=[
                "thezvi.substack.com",
                "x.com",
                "twitter.com",
                "www.youtube.com",
            ],
        )
        references = remove_duplicates(references)
        for ref in references:
            ref_dict: URLDict = {
                "url": ref,
                "harvest_timestamp": datestring(datetime.now()),
                "source": page["url"],
                "creation_date": page["creation_date"],
            }
            ref_dicts.append(ref_dict)

    return blogpost_dicts + ref_dicts


def remove_duplicates(strs: list[str]) -> list[str]:
    """Removes duplicate URLs while preserving order."""
    seen = set()
    return [str for str in strs if not (str in seen or seen.add(str))]


def extract_thezvi_date(url: str) -> str:
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        year, month, day = match.groups()
        dt = datetime(int(year), int(month), int(day))
        return datestring(dt)
    return "unknown"
