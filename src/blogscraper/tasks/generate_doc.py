from datetime import datetime

from blogscraper.content_viewer import show_page_content
from blogscraper.types import URLDict
from blogscraper.ui import console, infostr, select_urls, urlstr, warnstr
from blogscraper.utils.google_interface import create_google_doc, write_to_google_doc
from blogscraper.utils.time_utils import datestring


def generate_doc(
    ranged_urls: list[URLDict], start_day: datetime, end_day: datetime, format: str
) -> None:
    """Generates a document (Google Doc or Markdown) with selected blog content.

    Args:
        ranged_urls (list[URLDict]): List of URLs with metadata.
        start_day (datetime): Start date for the document title.
        end_day (datetime): End date for the document title.
        format (str): Output format, either "Google Doc" or "Markdown".

    Raises:
        ValueError: If an unsupported format is specified.
    """
    selected_urls = select_urls(ranged_urls)

    human_start = datestring(start_day, human=True)
    human_end = datestring(end_day, human=True)
    title = f"{human_start} - {human_end} blog scrape"

    if format == "Google Doc":
        document_content = prepare_google_doc_content(
            selected_urls, max_length=1_000_000
        )
        doc_id, doc_url = create_google_doc(title)
        write_to_google_doc(doc_id, document_content)
        console.print(infostr(f"Created Google doc: {urlstr(doc_url)}"))

    elif format == "Markdown":
        document_content = prepare_google_doc_content(
            selected_urls, max_length=3_000_000
        )
        markdown_filename = f"{title.replace(' ', '_')}.md"
        with open(markdown_filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# {title}\n\n{document_content}")

        console.print(infostr(f"Created Markdown file: {markdown_filename}"))

    else:
        raise ValueError(f"Unsupported document format: '{format}'")


def prepare_google_doc_content(
    selected_urls: list[str], max_length: int = 999_999_999
) -> str:
    """Prepares the content for the Google Document."""
    text = "<!-- This document is a set of blog posts focused on AI innovations -->\n\n"
    text += "<!-- TABLE OF CONTENTS -->\n\n"
    text += "\n".join(selected_urls) + "\n\n"

    for i, url in enumerate(selected_urls, start=1):
        contents = show_page_content(url, to_string=True)
        text += contents
        console.print(
            infostr(f"Adding {i}/{len(selected_urls)} (len={len(contents)}): {url}")
        )

        if (len_so_far := len(text)) > max_length:
            console.print(
                warnstr(
                    f"This document may be too big ({len_so_far}).\n"
                    + "Not appendng more documents.\n"
                    + "Table of contents will be inconsistent."
                )
            )
            break

    return text
