from urllib.parse import urljoin


def normalize_url(base_url: str, link: str) -> str:
    """
    Converts a relative URL to an absolute URL using the base URL.

    Args:
        base_url (str): The base URL of the website.
        link (str): The URL to be normalized.

    Returns:
        str: The normalized absolute URL.
    """
    return urljoin(base_url, link)
