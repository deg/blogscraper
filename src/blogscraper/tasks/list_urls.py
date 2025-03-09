from blogscraper.types import URLDict
from blogscraper.ui import console


def list_urls(ranged_urls: list[URLDict]) -> None:
    """Displays a list of URLs."""
    for url_dict in ranged_urls:
        console.print(f"[blue3]{url_dict['url']}[/blue3]")
