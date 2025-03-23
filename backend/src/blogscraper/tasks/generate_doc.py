import re

from degel_python_utils import setup_logger

from blogscraper.types import FilterRangeQuery, URLDict
from blogscraper.ui import urlstr
from blogscraper.utils.google_interface import create_google_doc, write_to_google_doc
from blogscraper.utils.mongodb_helpers import filter_posts
from blogscraper.utils.time_utils import datestring

logger = setup_logger(__name__)


def generate_doc(query: FilterRangeQuery, format: str) -> str:
    """Generates a document (Google Doc or Markdown) with selected blog content.

    Args:
        posts (list[URLDict]): List of URLs with metadata.
        start_day (datetime): Start date for the document title.
        end_day (datetime): End date for the document title.
        format (str): Output format, either "Google Doc" or "Markdown".

    Raises:
        ValueError: If an unsupported format is specified.
    """
    posts = filter_posts(
        start_dt=query.start_dt,
        end_dt=query.end_dt,
        source=query.source,
        match_string=query.match_string,
    )

    human_start = datestring(query.start_dt, human=True)
    human_end = datestring(query.end_dt, human=True)
    filter_title = f" filtered by '{query.match_string}'" if query.match_string else ""
    title = f"{human_start} - {human_end} blog scrape{filter_title}"

    header_text = (
        "<!-- \n"
        "This document is a set of blog posts focused on AI innovations. It "
        f"includes blog posts from {human_start} through {human_end}{filter_title}."
        "\n -->\n\n"
    )

    max_length = 1_000_000 if format == "Google Doc" else 3_000_000
    document_content = extract_docs_contents(header_text, posts, max_length=max_length)

    if format == "Google Doc":
        doc_id, doc_url = create_google_doc(title)
        write_to_google_doc(doc_id, document_content)
        logger.info(f"Created Google doc: {urlstr(doc_url)}")
        return doc_url

    elif format == "Markdown":
        return f"# {title}\n\n{document_content}"

    else:
        raise ValueError(f"Unsupported document format: '{format}'")


def extract_docs_contents(
    header_text: str,
    posts: list[URLDict],
    max_length: int = 999_999_999,
) -> str:
    """Prepares the content for the Google Document."""

    kept_urls = []
    body_text = ""

    for i, post in enumerate(posts, start=1):
        url = post.url
        contents = post.formatted_content
        kept_urls.append(url)
        body_text += contents
        logger.minor(f"Adding {i}/{len(posts)} (len={len(contents)}): {url}")

        if (len_so_far := len(body_text)) > max_length:
            logger.warning(
                f"This document may be too big ({len_so_far}).\n"
                "Not appendng more documents."
            )
            break

    text = header_text
    text += "<!-- TABLE OF CONTENTS -->\n\n"
    text += "\n".join(kept_urls) + "\n\n"
    text += body_text
    return text


def match_filter(contents: str, filter_str: str) -> bool:
    """
    Tests if a multiline string `contents` contains the `filter_str`,
    treating `filter_str` as a case-insensitive regex pattern if applicable.

    Args:
        contents (str): The text to search in.
        filter_str (str): The user-provided string, which may be a regex pattern.

    Returns:
        bool: True if `contents` match the filter criteria.
    """
    try:
        return bool(re.search(filter_str, contents, re.IGNORECASE | re.DOTALL))
    except re.error:
        return filter_str.lower() in contents.lower()
