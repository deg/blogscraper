from dataclasses import dataclass
from typing import Callable, TypedDict


class URLDict(TypedDict):
    url: str
    source: str
    creation_date: str
    harvest_timestamp: str


@dataclass
class Scraper:
    name: str
    function: Callable[[], list[URLDict]]
