import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel

from blogscraper.types import Scraper

console = Console()


def display_welcome() -> None:
    console.print(Panel("Welcome to the Blog Scraper!", title="Blog Scraper"))


def confirm_action(message: str) -> bool:
    response = questionary.confirm(message, auto_enter=False).ask()
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
