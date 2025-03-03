from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.scrapers.nathanbenaich import scrape_cliffnotes, scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import URLDict
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)

console = Console()

# Allow long lines
# flake8: noqa: E501

PROMPT_PREFIX = """
# Summarize Recent AI and Software Development Blog Posts

Here are some very recent blog posts, focused on AI and software development.  Each of these posts typically discusses multiple current stories in great detail.
"""

PROMPT_SUFFIX = """

## Your Task:

Read the blog post webpages referenced by each of these URLs.

Find the most important stories in each of these posts.

Create a **comprehensive report** aimed at **software practitioners**. Focus on the ten
to twenty most compelling stories.


## Workflow & Requirements:

1. **Read blog posts**

Use your web-browsing capabilities to read each of these web pages. You must read the actual pages. Do not try to extrapolate or guess from the page titles.

2. **Extract & Organize Stories**

   - Identify and extract multiple **distinct stories, insights, or notable points** from each post.

3. **Write the Report**

   - Select the most compelling stories.
   - For each selected story:
     - Create a one-paragraph **summary** of its key points.
     - **Immediately** follow the summary with the **title of the source blog post** and its **URL** in parentheses.
     - You must summarize only stories from the blog posts that I've shared with you.
     - You must follow each summary with a reference (title and URL) from the list that I shared above. No other URLs are acceptable.
   - Ensure the report is **structured and well-organized** for easy readability.

## Formatting Expectations:

- **Each story should be clearly delineated.**
- **Source titles and URLs should be placed immediately after each corresponding story in parentheses.**
- **Each story must have a source title and URL from the provided list.**
- **Use the exact format shown in the example below.**

## Example of Story Formatting:

<START OF SAMPLE DESIRED RESULT>

*Grok 3 Beta: xAI's Advanced AI for Reasoning and Problem-Solving*:

xAI's Grok 3 Beta, powered by a 100k H100 cluster, is designed for reasoning, mathematics, coding, and instruction-following. It uses large-scale reinforcement learning to enhance problem-solving, including backtracking and self-correction. With an Elo score of 1402 in the Chatbot Arena and strong benchmark results (AIME'25: 93.3%, GPQA: 84.6%), Grok 3 rivals top AI models. It introduces a "Think" mode for transparent reasoning and includes a cost-efficient variant, Grok 3 mini.

(Source: "Your Guide To AI: March 2025" - https://nathanbenaich.substack.com/p/your-guide-to-ai-march-2025)

<END OF SAMPLE DESIRED RESULT>
"""


def main() -> None:
    console.print(Panel("Welcome to the Blog Scraper!", title="Blog Scraper"))

    # Ask the user if they want to scrape new URLs
    scrape = questionary.confirm("Do you want to scrape new URLs?").ask()

    if scrape:
        # Display choices for which sites to scrape, defaulting to all selected
        selected_sites = questionary.checkbox(
            "Select sites to scrape:",
            choices=[
                Choice("The Zvi", value="1", checked=True),
                Choice("Simon Willison", value="2", checked=True),
                Choice("Nathan Benaich", value="3", checked=True),
                Choice("Cliffnotes", value="4", checked=True),
            ],
        ).ask()

        results = run_scrapers(selected_sites)
    else:
        results = {"existing_urls": load_stored_urls()}

    # Ask if the user wants to generate an LLM prompt
    generate_prompt = questionary.confirm(
        "Do you want to generate an LLM prompt?"
    ).ask()

    if generate_prompt:
        # Ask for lookback days with validation
        while True:
            try:
                lookback_days = int(
                    questionary.text("Enter the number of days to look back:").ask()
                )
                break
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

        relevant = recent_urls(results["existing_urls"], lookback_days)
        print(f"{PROMPT_PREFIX}\n\n{generate_title_list(relevant)}\n\n{PROMPT_SUFFIX}")


def run_scrapers(selected_sites: list[str]) -> dict[str, list[URLDict]]:
    """
    Scrape blog entries from selected sites.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    existing_urls = load_stored_urls()

    # Scrape new URLs from selected sources
    all_new_urls = []
    if "1" in selected_sites:
        all_new_urls.extend(scrape_thezvi())
    if "2" in selected_sites:
        all_new_urls.extend(scrape_simonwillison())
    if "3" in selected_sites:
        all_new_urls.extend(scrape_nathanbenaich())
    if "4" in selected_sites:
        all_new_urls.extend(scrape_cliffnotes())

    # Deduplicate and save new URLs
    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)
    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
    }


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
    1. "Economics Roundup 5" - https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
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
        "Economics Roundup 5" - https://thezvi.wordpress.com/2025/02/25/economics-roundup-5/
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
