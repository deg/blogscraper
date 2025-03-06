"""Utility functions for working with datetimes"""

from datetime import datetime, timezone


def datestring(dt: datetime) -> str:
    """Converts a datetime object to an ISO 8601 formatted string with UTC timezone.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        str: The ISO-formatted datetime string with second-level precision.
    """
    return dt.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
