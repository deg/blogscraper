# Blogscraper

**Blogscraper** is a Python-based tool designed to scrape and summarize recent articles
from selected AI and software development blogs. It extracts interesting URLs, fetches
their content, and optionally prepares the data for further analysis or for input into a
Large Language Model (LLM).

This project also began as an experiment with the LLM-aided
[project design ideas](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/)
published by Harper Reed, and with [Cursor](https://www.cursor.com/) and
[SpecStory](https://specstory.com/).

---

## Motivation

In the rapidly evolving fields of AI and software development, staying updated with the
latest information is crucial yet challenging. New articles, tutorials, and insights are
published daily across numerous platforms, making it difficult to keep
track. **Blogscraper** addresses this challenge by automating the process of collecting
and summarizing recent blog posts, ensuring that users have timely access to relevant
information without the need for manual tracking.

---

## Project Structure

```plaintext
blogscraper/
├── src/
│   └── blogscraper/             # Proejct source files (details here may be out-of-date)
│       ├── scrapers/            # Blog-specific scraper modules
│       ├── utils/               # Utility modules
│       ├── content_viewer.py    # Fetch and display page content
│       ├── main.py              # Entry point for CLI
│       ├── prompt.py            # Prompt templates for LLM
│       ├── scraper_manager.py   # Orchestrate scraping tasks
│       ├── types.py             # Type definitions
│       └── ui.py                # CLI user interactions
├── tests/                       # Unit tests (still superficial.) [HELP-WANTED]
├── .github/workflows/ci.yml     # CI configuration
├── Makefile                     # Common tasks automation
├── pyproject.toml               # Dependency management with Poetry
└── README.md                    # This documentation
```

---

## Getting Started

### Prerequisites

- Python >= 3.11
- [Poetry](https://python-poetry.org/) (dependency management)

### Installation

Clone the repository:

```bash
git clone git@github.com:deg/blogscraper.git
cd blogscraper
```

Set up the environment:

```bash
make setup-dev-env
```

This command will install dependencies, set up Git hooks, and prepare your environment.

---

## Running Blogscraper

### Execution

Start the program with Make:

```bash
make run
```

This will take you into a simple CLI UI:

```plaintext
$ make run
🚀 Running the application...
poetry run python -m blogscraper.main
╭────────────────────────────────────── Blog Scraper ──────────────────────────────────────╮
│ Welcome to the Blog Scraper!                                                             │
│                                                                                          │
│ This tool gathers and summarizes several popular AI-related blogs,                       │
│ using a variety of web-scraping and AI tools.                                            │
│                                                                                          │
│ Started March 2025, by David Goldfarb. Questions to deg@degel.com                        │
│                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
? Do you want to scrape new URLs? Yes
? Erase old DB and start fresh? No
? Select sites to scrape: done (4 selections)
Fetching and parsing URLs from https://thezvi.wordpress.com/
Fetching and parsing URLs from https://thezvi.wordpress.com/2025/03/
...
Fetching and parsing URLs from https://simonwillison.net/
Fetching and parsing URLs from https://nathanbenaich.substack.com/archive?sort=new
Fetching and parsing URLs from https://newsletter.cliffnotes.ai/
? Enter the number of days to look back (default is 7):
? Do you want to see the page contents of recent blogs? No
? Do you want a list of the URLs? No
? Do you want to generate a consolidated document? No
? Do you want to generate an LLM prompt? No

```

Blogscraper search for recent blog posts from a number of sites. The list is currently
hardcoded but extensible, with custom scrapers for each site. We are looking to automate
this process. [HELP-WANTED].

You can then filter this list to retain only the most recent posts.

Finally, you can output these in one or more formats:

## Blogscraper Outputs

Blogscraper provides several output formats to accommodate different workflows:

- **Full page contents**: The main content of the blog posts, in Markdown format, and
  with extraneous page wrappers removed.
- **List of URLs**: A simple list of scraped URLs that can be used for further
  exploration or as input to other tools.
- **Consolidated document**: Generate a Google Doc with all the blog posts' content and
  header data. This is a great format to pass into tools like
  [NotebookLM](https://notebooklm.google.com/).
- **LLM Prompts**: This is still experimental and only marginally useful. Generate an
  LLM prompt designed to guide AI models in processing and summarizing blog
  content. [HELP-WANTED]

---

## Available Commands in the Makefile

Use the Makefile to perform common tasks:

```bash
make help
```

Commands include:

- `make setup-dev-env`: Prepare your development environment
- `make run`: Execute the main application
- `make lint`: Check code quality using Black, isort, Ruff, Pyright, and MyPy
- `make test`: Run unit tests (Still rudimentary) [HELP-WANTED]
- `make coverage`: Check test coverage and ensure it meets the required threshold
- `make outdated`: Show outdated dependencies
- `make as-llm-input`: Generate a copy of the repository, suitable for passing to LLM tools

---

## Join the Project!

We’d love for you to contribute! If you find Blogscraper useful and have ideas for
improvements, feel free to fork the [repository](https://github.com/deg/blogscraper) or
open a PR.

Suggestions, bug reports, and feedback are always welcome!

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Author

David Goldfarb - [deg@degel.com](mailto:deg@degel.com)

