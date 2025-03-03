import argparse
from datetime import datetime, timedelta, timezone

from blogscraper.scrapers.nathanbenaich import scrape_nathanbenaich
from blogscraper.scrapers.simonwillison import scrape_simonwillison
from blogscraper.scrapers.thezvi import scrape_thezvi
from blogscraper.types import URLDict
from blogscraper.utils.storage import (
    deduplicate_urls,
    load_stored_urls,
    save_stored_urls,
)


def main() -> None:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the blog scrapers.")
    parser.add_argument(
        "--lookback",
        type=int,
        help="Print URLs collected within the last N days",
    )
    parser.add_argument(
        "--scrape",
        action="store_true",
        default=True,
        help="Run scrapers to collect new URLs (default: True)",
    )
    parser.add_argument(
        "--no-scrape",
        dest="scrape",
        action="store_false",
        help="Do not run scrapers to collect new URLs",
    )
    args = parser.parse_args()

    # Run scrapers and process URLs if --scrape is true
    if args.scrape:
        results = run_scrapers()
    else:
        results = {"existing_urls": load_stored_urls()}

    # Handle the --lookback flag
    if args.lookback is not None:
        relevant = recent_urls(results["existing_urls"], args.lookback)
        print(
            f"""
# Summarize Recent AI and Software Development Blog Posts

I will provide a list of recent blog post URLs related to AI and software development.

## Your Task:

Summarize the key insights from all the provided blog posts into a **comprehensive
2,000-word report** aimed at **software practitioners**. Include only the ten most
interesting stories.

## Workflow & Requirements:

1. **Extract & Organize Stories**

   - Identify and extract multiple **distinct stories, insights, or notable points**
     from each post.

2. **Write the Report**

   - Choose the ten best stories.
   - Generate a one-paragraph **summary** of each chosen story, ensuring that each
     story text ends with the **URL of the source blog post**.
   - **Important:** Follow each extracted story immediately with the blog URL in
       parentheses**. It is very important that the blog URL should be one of the blog
       URLs that I will give you below. Each story must have a source blog URL.
   - The report should be **structured and well-organized**, making it easy for readers
     to follow.
   - It is very important that each story be followed by its blog URL.
   - It is very important that the blog URLs come only from the list I am supplying
     here.

## Formatting Expectations:

- **Each story should be clearly delineated.**
- **URLs should be placed immediately after each corresponding story in parentheses.**
- **Each story should have a URL**
- **Each URL should be real, and be taken from the list I am giving you below**

## Example of Story Formatting:

This is the precise format that you must use for each story:

<START OF FORMAT>
*Story Title*:
Brief description of the story's key points.
(Source:
<a href="https://thezvi.wordpress.com/2025/02/14/growing-LLM-storage/capacity">
https://thezvi.wordpress.com/2025/02/14/growing-LLM-storage/capacity</a>)
<END OF FORMAT>

## Here are the URLs to Process:

{generate_html_list(relevant)}

"""
        )


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


def run_scrapers() -> dict[str, list[URLDict]]:
    """
    Scrape blog entries from interesting sites.

    Returns:
        dict[str, list[URLDict]]: A dictionary of lists of new and existing URLs.
    """
    # Load existing URLs from urls.json
    existing_urls = load_stored_urls()

    # Scrape new URLs from different sources
    new_urls_thezvi = scrape_thezvi()
    new_urls_simonwillison = scrape_simonwillison()
    new_urls_nathanbenaich = scrape_nathanbenaich()

    # Combine all new URLs
    all_new_urls = new_urls_thezvi + new_urls_simonwillison + new_urls_nathanbenaich

    # Deduplicate and save new URLs
    unique_new_urls = deduplicate_urls(all_new_urls, existing_urls)
    save_stored_urls(existing_urls + unique_new_urls)
    return {
        "all_new_urls": all_new_urls,
        "unique_new_urls": unique_new_urls,
        "existing_urls": existing_urls,
    }


def generate_html_list(urls: list[URLDict]) -> str:
    """
    Generates an HTML list of <li> elements with <a> links to the URLs.

    Args:
        urls (list[URLDict]): A list of URLDict objects.

    Returns:
        str: A string containing the HTML list.
    """
    html_list = "\n"  # "<ul>\n"
    for url_dict in urls:
        url = url_dict["url"]
        html_list += f"{url}\n"
        # html_list += f'  <li><a href="{url}">{url}</a></li>\n'
    # html_list += "</ul>"
    return html_list


if __name__ == "__main__":  # pragma: no cover
    main()
