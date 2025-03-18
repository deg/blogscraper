from blogscraper.types import URLDict
from blogscraper.ui import console, urlstr


def list_urls(ranged_urls: list[URLDict]) -> None:
    """Displays a list of URLs."""
    for url_dict in ranged_urls:
        console.print(urlstr(url_dict.url))
