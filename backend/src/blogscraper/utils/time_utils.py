"""Utility functions for working with datetimes"""

from datetime import datetime, timezone


def datestring(dt: datetime, human: bool = False) -> str:
    """Converts a datetime object to a formatted string.

    Args:
        dt (datetime): The datetime object to convert.

        human (bool, optional): If True, returns a USA human-friendly
        format (e.g., "Feb 25, 2025").

    Returns:
        str: The formatted datetime string.

    """
    dt = dt.replace(tzinfo=timezone.utc)

    if human:
        return dt.strftime("%b %d, %Y")
    return dt.isoformat(timespec="seconds")
