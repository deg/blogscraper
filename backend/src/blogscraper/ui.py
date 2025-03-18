"""Handles user interaction for the Blogscraper CLI.

Provides functions for displaying messages, prompting user input,
and allowing interactive selections.
"""

from datetime import datetime, timezone

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.types import GDoc, Scraper, URLDict

console = Console()


def display_welcome() -> None:
    """Displays a welcome message when Blogscraper starts."""
    console.print(
        Panel(
            """Welcome to the Blog Scraper!

This tool gathers and summarizes several popular AI-related blogs,
using a variety of web-scraping and AI tools.

Started March 2025, by David Goldfarb. Questions to deg@degel.com
""",
            title="Blog Scraper",
        )
    )


def confirm_action(message: str, default: bool = True) -> bool:
    """Prompts the user with a yes/no confirmation question.

    Args:
        message (str): The confirmation question to ask the user.
        default (bool, optional): The default choice if the user presses Enter. Defaults
                to True.

    Returns:
        bool: True if the user confirms, False otherwise.

    """
    response = questionary.confirm(
        message, auto_enter=False, default=default
    ).unsafe_ask()
    return bool(response)


def select_scrapers(scrapers: list[Scraper]) -> list[str]:
    """Prompts the user to select which scrapers to run.

    Args:
        scrapers (list[Scraper]): A list of available scraper objects.

    Returns:
        list[str]: A list of selected scraper names.
    """
    response = questionary.checkbox(
        "Select sites to scrape:",
        choices=[
            Choice(scraper.name, value=str(index), checked=True)
            for index, scraper in enumerate(scrapers)
        ],
    ).unsafe_ask()
    return list(response)


def select_google_docs(docs: list[GDoc], action: str) -> list[GDoc]:
    """Prompts the user to select Google Docs from a list.

    Args:
        docs (list[GDoc]): A list of Google Documents.
        action (str): Reason for this list (for prompt).

    Returns:
        list[Gdoc]: A list of selected documents.
    """
    if not docs:
        print(f"⚠️ No documents available to {action}.")
        return []

    response = questionary.checkbox(
        f"Select Google Docs to {action}:",
        choices=[
            Choice(
                f"{doc.createdTime} - {doc.name} ({doc.url})", value=doc, checked=False
            )
            for doc in docs
        ],
    ).unsafe_ask()

    return response if response else []


def select_urls(
    urlDicts: list[URLDict], prompt: str = "Select blog URLs to save:"
) -> list[str]:
    """Prompts the user to select which blog URLs to process.

    Args:
        urlDicts (list[URLDict]): A list of URL metadata dictionaries.

    Returns:
        list[str]: A list of selected URLs.
    """
    response = questionary.checkbox(
        prompt,
        choices=[
            Choice(urlDict.url, value=urlDict.url, checked=True) for urlDict in urlDicts
        ],
    ).unsafe_ask()
    return list(response)


def input_text(message: str, default: str) -> str:
    """
    Prompts the user to enter a text input with a default value.

    Args:
        message (str): The prompt message to display.
        default (str): The default value to prefill in the input.

    Returns:
        str: The user-provided input.
    """
    response = questionary.text(message, default=default).unsafe_ask()
    return response or ""


def input_date(message: str, default_date: datetime) -> datetime:
    """Prompts the user for a date using questionary for a friendlier CLI experience.

    Args:
        message (str): The prompt message to display.
        default_date (datetime): The default date to prefill in the input.

    Returns:
        datetime: The selected date.
    """
    while True:
        date_str = questionary.text(
            f"{message} (default: {default_date.strftime('%Y-%m-%d')})",
            default=default_date.strftime("%Y-%m-%d"),
        ).unsafe_ask()

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )

            return date_obj
        except ValueError:
            console.print(
                errstr(
                    "Invalid date format. " + "Please enter a valid date (YYYY-MM-DD)."
                )
            )


def minor_infostr(msg: str) -> str:
    """Format string to show as info on console"""
    return f"[grey19]{msg}[/grey19]"


def infostr(msg: str) -> str:
    """Format string to show as info on console"""
    return f"[bold]{msg}[/bold]"


def warnstr(msg: str) -> str:
    """Format string to show as warning on console"""
    return f"[red]{msg}[/red]"


def errstr(msg: str) -> str:
    """Format string to show as error on console"""
    return f"[bold][red]{msg}[/red][/bold]"


def urlstr(url: str) -> str:
    """Format string to show as a URL on console"""
    return f"[blue3][link={url}]{url}[/link][blue3]"
