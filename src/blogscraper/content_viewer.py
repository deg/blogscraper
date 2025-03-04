import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from rich.console import Console
from rich.panel import Panel

console = Console()


def show_page_content(url: str) -> None:
    """
    Fetch and display the content of a webpage as Markdown.

    Args:
        url (str): The URL of the webpage to fetch.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        html_content = str(soup)
        markdown_content = md(html_content)

        # Allow up to one blank line between paragraphs
        cleaned_lines = []
        for line in markdown_content.splitlines():
            if line.strip() or (cleaned_lines and cleaned_lines[-1]):
                cleaned_lines.append(line)
        cleaned_markdown_content = "\n".join(cleaned_lines)
        console.print(Panel(cleaned_markdown_content, title=f"Content of {url}"))

    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]")
