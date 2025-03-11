from datetime import datetime

from blogscraper.content_viewer import show_page_content
from blogscraper.types import URLDict
from blogscraper.ui import console, infostr, select_urls, urlstr, warnstr
from blogscraper.utils.google_interface import create_google_doc, write_to_google_doc
from blogscraper.utils.time_utils import datestring


def generate_doc(
    ranged_urls: list[URLDict], start_day: datetime, end_day: datetime
) -> None:
    """Generates a Google Document with selected blog content."""
    selected_urls = select_urls(ranged_urls)
    document_content = prepare_google_doc_content(selected_urls)

    human_start = datestring(start_day, human=True)
    human_end = datestring(end_day, human=True)

    doc_id, doc_url = create_google_doc(f"{human_start} - {human_end} blog scrape")
    write_to_google_doc(doc_id, document_content)
    console.print(infostr(f"Created Google doc: {urlstr(doc_url)}"))


def prepare_google_doc_content(selected_urls: list[str]) -> str:
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

        if (len_so_far := len(text)) > 1_000_000:
            console.print(
                warnstr(
                    f"This document is getting long ({len_so_far}. "
                    + "It may be too big for Google Docs).\n"
                    + "Not appendng more documents.\n"
                    + "Table of contents will be inconsistent."
                )
            )
            break

    return text
