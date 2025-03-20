"""Defines type structures for Blogscraper.

Provides type annotations and data structures used throughout the project.

Usage:
    These types help enforce consistency in scraper functions and data handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from bson import ObjectId


@dataclass
class URLDict:
    """Represents structured metadata for a scraped blog URL.

    Attributes:
        url (str): The URL of the blog post.
        clean_url (str): The URL of the blog post with tracking params, etc., removed
        source (str): The name of the blog or website.
        creation_date (datetime): The date the post was published.
        harvest_timestamp (datetime): The timestamp when the URL was scraped.
    """

    url: str
    clean_url: str
    source: str
    creation_date: datetime
    harvest_timestamp: datetime
    formatted_content: str


@dataclass
class GDoc:
    """Represents metadata for a Google Document."""

    id: str
    name: str
    createdTime: str
    modifiedTime: str
    url: str


@dataclass
class Scraper:
    """Represents a blog scraper with a name and associated scraping function.

    Attributes:
        name (str): The name of the scraper.
        base_url (str): The base URL of the blog.
        function (Callable[[Scraper], list[URLDict]]): A function that scrapes URLs
            using the scraper instance.
    """

    name: str
    base_url: str
    function: Callable[["Scraper", Callable[[str], None] | None], list[ObjectId]]
