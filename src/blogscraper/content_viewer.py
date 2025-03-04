import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel

console = Console()


def show_page_content(url: str) -> None:
    """
    Fetch and display the content of a webpage.

    Args:
        url (str): The URL of the webpage to fetch.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        console.print(Panel(text, title=f"Content of {url}"))
    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")
