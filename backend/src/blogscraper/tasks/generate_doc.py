import re
from datetime import datetime

from degel_python_utils import setup_logger

from blogscraper.types import URLDict
from blogscraper.ui import urlstr
from blogscraper.utils.google_interface import create_google_doc, write_to_google_doc
from blogscraper.utils.time_utils import datestring

logger = setup_logger(__name__)
# XXpXXylint: disable=logging-format-interpolation


def generate_doc(
    posts: list[URLDict], start_day: datetime, end_day: datetime, format: str
) -> str:
    """Generates a document (Google Doc or Markdown) with selected blog content.

    Args:
        posts (list[URLDict]): List of URLs with metadata.
        start_day (datetime): Start date for the document title.
        end_day (datetime): End date for the document title.
        format (str): Output format, either "Google Doc" or "Markdown".

    Raises:
        ValueError: If an unsupported format is specified.
    """
    filter_str = None

    human_start = datestring(start_day, human=True)
    human_end = datestring(end_day, human=True)
    filter_title = f" filtered by '{filter_str}'" if filter_str else ""
    title = f"{human_start} - {human_end} blog scrape{filter_title}"

    header_text = (
        "<!-- \n"
        "This document is a set of blog posts focused on AI innovations. It "
        f"includes blog posts from {human_start} through {human_end}{filter_title}."
        "\n -->\n\n"
    )

    max_length = 1_000_000 if format == "Google Doc" else 3_000_000
    document_content = prepare_google_doc_content(
        header_text, posts, max_length=max_length, filter_str=filter_str
    )

    if format == "Google Doc":
        doc_id, doc_url = create_google_doc(title)
        write_to_google_doc(doc_id, document_content)
        logger.info(f"Created Google doc: {urlstr(doc_url)}")
        return doc_url

    elif format == "Markdown":
        # - markdown_filename = f"{title.replace(' ', '_')}.md"
        # - with open(markdown_filename, "w", encoding="utf-8") as md_file:
        # -     md_file.write(f"# {title}\n\n{document_content}")
        # - logger.info(f"Created Markdown file: {markdown_filename}")
        return document_content

    else:
        raise ValueError(f"Unsupported document format: '{format}'")


def prepare_google_doc_content(
    header_text: str,
    posts: list[URLDict],
    max_length: int = 999_999_999,
    filter_str: str | None = None,
) -> str:
    """Prepares the content for the Google Document."""

    kept_urls = []
    body_text = ""

    for i, post in enumerate(posts, start=1):
        url = post.url
        contents = post.formatted_content
        if not filter_str or match_filter(contents, filter_str):
            kept_urls.append(url)
            body_text += contents
            logger.info(f"Adding {i}/{len(posts)} (len={len(contents)}): {url}")
        else:
            logger.minor(f"Skipping {i}/{len(posts)}: {url}")

        if (len_so_far := len(body_text)) > max_length:
            logger.warning(
                f"This document may be too big ({len_so_far}).\n"
                "Not appendng more documents.\n"
                "Table of contents will be inconsistent."
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
