"""Defines type structures for Blogscraper.

Provides type annotations and data structures used throughout the project.

Usage:
    These types help enforce consistency in scraper functions and data handling.
"""

from dataclasses import dataclass
from typing import Callable, TypedDict


# [TODO] Convert this to a dataclass too
class URLDict(TypedDict):
    """Represents structured metadata for a scraped blog URL.

    Attributes:
        url (str): The URL of the blog post.
        source (str): The name of the blog or website.
        creation_date (str): The date the post was published.
        harvest_timestamp (str): The timestamp when the URL was scraped.
    """

    url: str
    source: str
    creation_date: str
    harvest_timestamp: str


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
        function (Callable[[], list[URLDict]]): A function that scrapes URLs and
        returns structured metadata.
    """

    name: str
    function: Callable[[], list[URLDict]]
