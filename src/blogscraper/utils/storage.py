import json
import os


def load_stored_urls():
    file_path = os.path.join("data", "urls.json")

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


def save_stored_urls(urls_list: list[dict]):
    file_path = os.path.join("data", "urls.json")

    with open(file_path, "w") as file:
        json.dump(urls_list, file, indent=4)


def deduplicate_urls(new_urls: list[dict], existing_urls: list[dict]) -> list[dict]:
    """
    Returns a list of URLs from new_urls that are not present in existing_urls.

    Args:
        new_urls (list[dict]): A list of dictionaries, each with a "url" key.
        existing_urls (list[dict]): A list of dictionaries, each with a "url" key.

    Returns:
        list[dict]: A list of dictionaries from new_urls with unique "url" values not
                    found in existing_urls.
    """
    existing_urls_set = {url_dict["url"] for url_dict in existing_urls}
    return [
        url_dict for url_dict in new_urls if url_dict["url"] not in existing_urls_set
    ]
