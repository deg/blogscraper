"""Defines type structures for Blogscraper.

Provides type annotations and data structures used throughout the project.

Usage:
    These types help enforce consistency in scraper functions and data handling.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable

from bson import ObjectId
from fastapi import HTTPException, Query


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


class FilterRangeQuery:
    """Query parameters for filtering document selection."""

    def __init__(
        self,
        start_date: date = Query(..., description="Start date (inclusive)"),
        end_date: date = Query(..., description="End date (inclusive)"),
        source: str | None = Query(None, description="Filter by source"),
        match_string: str | None = Query(
            None, description="Regex to match in post content"
        ),
    ):
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="start_date must be before end_date."
            )
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.match_string = match_string

    @property
    def start_dt(self) -> datetime:
        return datetime.combine(self.start_date, datetime.min.time())

    @property
    def end_dt(self) -> datetime:
        return datetime.combine(self.end_date, datetime.max.time())
