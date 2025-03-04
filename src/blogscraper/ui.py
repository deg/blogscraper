import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.types import Scraper

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


def input_lookback_days() -> int:
    while True:
        try:
            return int(questionary.text("Enter the number of days to look back:").ask())
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
