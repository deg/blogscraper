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
