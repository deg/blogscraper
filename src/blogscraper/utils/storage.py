import json
import os

from blogscraper.types import URLDict

DATA_DIRECTORY = "data"
URLS_FILENAME = "urls.json"


def get_file_path() -> str:
    """
    Constructs the file path for the URLs storage file and ensures the directory exists.
    """
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    return os.path.join(DATA_DIRECTORY, URLS_FILENAME)


def load_stored_urls() -> list[URLDict]:
    file_path = get_file_path()

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as file:
        try:
            data = json.load(file)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    return []


def save_stored_urls(urls_list: list[URLDict]) -> None:
    file_path = get_file_path()
    with open(file_path, "w") as file:
        json.dump(urls_list, file, indent=4)


def deduplicate_urls(
    new_urls: list[URLDict], existing_urls: list[URLDict]
) -> list[URLDict]:
    """
    Returns a list of URLs from new_urls that are not present in existing_urls.

    Args:
        new_urls (list[URLDict]): A list of dictionaries, each with a "url" key.
        existing_urls (list[URLDict]): A list of dictionaries, each with a "url" key.

    Returns:
        list[URLDict]: A list of dictionaries from new_urls with unique "url" values not
                    found in existing_urls.
    """
    existing_urls_set = {url_dict["url"] for url_dict in existing_urls}
    seen_urls = set()
    unique_new_urls = []

    for url_dict in new_urls:
        url = url_dict["url"]
        if url not in seen_urls and url not in existing_urls_set:
            seen_urls.add(url)
            print(f"Adding {url}")
            unique_new_urls.append(url_dict)

    return unique_new_urls


def clear_stored_urls() -> None:
    """
    Clears all stored URLs from the storage.
    """
    file_path = get_file_path()
    with open(file_path, "w") as file:
        file.write("[]")  # Write an empty list to clear the file
