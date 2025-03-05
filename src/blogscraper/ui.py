import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.types import Scraper, URLDict

console = Console()


def display_welcome() -> None:
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
    response = questionary.confirm(message, auto_enter=False, default=default).ask()
    return bool(response)


def select_scrapers(scrapers: list[Scraper]) -> list[str]:
    response = questionary.checkbox(
        "Select sites to scrape:",
        choices=[
            Choice(scraper.name, value=str(index), checked=True)
            for index, scraper in enumerate(scrapers)
        ],
    ).ask()
    return list(response)


def select_urls(urlDicts: list[URLDict]) -> list[str]:
    response = questionary.checkbox(
        "Select blog URLs to save:",
        choices=[
            Choice(urlDict["url"], value=urlDict["url"], checked=True)
            for urlDict in urlDicts
        ],
    ).ask()
    return list(response)


def input_lookback_days() -> int:
    while True:
        try:
            response = questionary.text(
                "Enter the number of days to look back (default is 7):"
            ).ask()
            if not response.strip():
                return 7
            return int(response)
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
