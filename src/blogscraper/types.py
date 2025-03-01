from typing import TypedDict


class URLDict(TypedDict):
    url: str
    harvest_timestamp: str
    source: str
    creation_date: str
    # Add other fields if necessary, e.g., timestamp: str, source: str
