"""Handles storage and retrieval of scraped blog URLs.

Provides functions to persist extracted URLs in a JSON file, ensuring deduplication
and retrieval of previously stored data.

Storage location:
    - Data is stored in `<ROOT>/data/urls.json`.
    - The data directory is created if it does not exist.

Usage:
    This module is used by scrapers to maintain a history of discovered blog posts,
    avoiding redundant re-processing of already scraped URLs.
"""

import json
import os

from blogscraper.types import URLDict

DATA_DIRECTORY = "data"
URLS_FILENAME = "urls.json"


def get_file_path() -> str:
    """Constructs the file path for the URLs storage file and ensures the directory
    exists.

    Returns:
        str: The full path to the storage file.

    """
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    return os.path.join(DATA_DIRECTORY, URLS_FILENAME)


def load_stored_urls() -> list[URLDict]:
    """Loads stored URLs from the JSON file.

    Returns:
        list[URLDict]: A list of stored URLs as URLDicts. Returns an empty list if the
        file does not exist or is corrupted.

    """
    file_path = get_file_path()

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as file:
        try:
            data = json.load(file)
            if isinstance(data, list):
                return [URLDict(**entry) for entry in data]
        except json.JSONDecodeError:
            pass

    return []


def save_stored_urls(urls_list: list[URLDict]) -> None:
    """Saves a list of URLs to the storage file, overwriting any existing data.

    Args:
        urls_list (list[URLDict]): A list of dictionaries containing URL data.
    """
    file_path = get_file_path()
    with open(file_path, "w") as file:
        json.dump([url_dict.__dict__ for url_dict in urls_list], file, indent=4)


def deduplicate_urls(
    new_urls: list[URLDict], existing_urls: list[URLDict]
) -> list[URLDict]:
    """Filters out URLs that are already present in the existing storage.

    Args:
        new_urls (list[URLDict]): A list of newly scraped URL dicts.
        existing_urls (list[URLDict]): A list of previously stored dicts.

    Returns:
        list[URLDict]: A list of dicts of unique URLs that are not present in the
        existing storage.

    """
    existing_urls_set = {url_dict.url for url_dict in existing_urls}
    seen_urls = set()
    unique_new_urls = []

    for url_dict in new_urls:
        url = url_dict.url
        if url not in seen_urls and url not in existing_urls_set:
            seen_urls.add(url)
            print(f"Adding {url}")
            unique_new_urls.append(url_dict)

    return unique_new_urls


def clear_stored_urls() -> None:
    """Clears all stored URLs by overwriting the storage file with an empty list."""
    file_path = get_file_path()
    with open(file_path, "w") as file:
        file.write("[]")  # Write an empty list to clear the file
