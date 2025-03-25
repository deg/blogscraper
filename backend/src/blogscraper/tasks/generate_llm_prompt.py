from urllib.parse import urlparse

from blogscraper.prompt import promptPrefix, promptSuffix
from blogscraper.types import FilterRangeQuery, URLDict
from blogscraper.utils.mongodb_helpers import filter_posts


def generate_llm_prompt(query: FilterRangeQuery) -> str:
    """Generates an LLM prompt based on the scraped data."""
    posts = filter_posts(
        start_dt=query.start_dt,
        end_dt=query.end_dt,
        source=query.source,
        match_string=query.match_string,
    )
    return (
        f"{promptPrefix(query)}\n\n"
        f"{generate_title_list(posts)}\n\n"
        f"{promptSuffix(query)}"
    )


def generate_title_list(urls: list[URLDict]) -> str:
    """Returns a numbered list of titles and URLs, e.g.,
    1. "Economics Roundup 5" -
       https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    2. ...

    Args:
        urls (list[URLDict]): A list of URLDict objects containing URLs and metadata.

    Returns:
        str: A formatted string listing numbered titles and URLs.
    """
    lines = []
    for i, url_dict in enumerate(urls, start=1):
        formatted = url_to_title_string(url_dict.url)
        lines.append(f"{i}. {formatted}")
    return "\n".join(lines)


def url_to_title_string(url: str) -> str:
    """
    Convert a URL like
        https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
    into a string like
        "Economics Roundup 5" -
         https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/

    Args:
        url (str): The URL to extract a title from.

    Returns:
        str: A formatted title extracted from the URL.
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
