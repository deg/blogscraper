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
