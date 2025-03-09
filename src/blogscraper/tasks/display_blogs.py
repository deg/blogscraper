from blogscraper.content_viewer import show_page_content
from blogscraper.types import URLDict
from blogscraper.ui import confirm_action


def display_blogs(ranged_urls: list[URLDict]) -> None:
    """Displays blog contents for selected URLs."""
    for url_dict in ranged_urls:
        if confirm_action(f"See content of {url_dict['url']}?"):
            show_page_content(url_dict["url"], to_string=False)
