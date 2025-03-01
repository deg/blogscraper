This file is a merged representation of the entire codebase, combined into a single document by Repomix. The content has been processed where security check has been disabled.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information

## Additional Info

# Directory Structure
```
.github/
  workflows/
    ci.yml
src/
  blogscraper/
    utils/
      __init__.py
      helpers.py
    __init__.py
    main.py
tests/
  test_helpers.py
  test_main.py
.gitignore
.pre-commit-config.yaml
LICENSE
Makefile
pyproject.toml
README.md
spec.md
```

# Files

## File: .github/workflows/ci.yml
````yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install
      - name: Run linters
        run: |
          poetry run black --check .
          poetry run isort --check-only .
          poetry run flake8 .
          poetry run mypy .
      - name: Run tests with coverage
        run: |
          poetry run pytest --cov=.
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
````

## File: src/blogscraper/utils/__init__.py
````python
# This file is intentionally left blank.
````

## File: src/blogscraper/utils/helpers.py
````python
def greet(name: str) -> str:
    return f"Hello, {name}!"
````

## File: src/blogscraper/__init__.py
````python
# This file is intentionally left blank.
````

## File: src/blogscraper/main.py
````python
from blogscraper.utils.helpers import greet


def main() -> None:
    name = "World"
    message = greet(name)
    print(message)  # "Hello, World!"


if __name__ == "__main__":  # pragma: no cover
    main()
````

## File: tests/test_helpers.py
````python
from blogscraper.utils.helpers import greet


def test_greet() -> None:
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"
````

## File: tests/test_main.py
````python
from pytest import CaptureFixture

from blogscraper.main import main


def test_example() -> None:
    assert 1 + 1 == 2


def test_main(capsys: CaptureFixture[str]) -> None:
    main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
````

## File: .gitignore
````
# Python
*.class
*.egg
*.egg-info/
*.log
*.pdb
*.py[cod]
*.pyd
*.pyo
.coverage
__pycache__/
build/
dist/
html/cov/

# Virtual Environments
.venv/

# Jupyter Notebooks (if any are used later)
.ipynb_checkpoints

# VS Code Settings
# .vscode/

# OS-specific files
.DS_Store
Thumbs.db

# Media Files (optional - if you don’t want to track large video files)
*.mp4
*.mov
*.avi
*.mkv

# DeepFace Cached Models
# ~/.deepface/
````

## File: .pre-commit-config.yaml
````yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
````

## File: LICENSE
````
MIT License

Copyright (c) 2025 David Goldfarb <deg@degel.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
````

## File: Makefile
````
# Use Bash for shell commands
SHELL := /bin/bash

# Project Name
PROJECT_NAME := "blogscraper"

.DEFAULT_GOAL := help

# Show this help message
.PHONY: help
help:
	@echo -e "\033[1;34mUsage:\033[0m make [target]"
	@echo ""
	@echo -e "\033[1;36mTargets:\033[0m"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	    helpMessage = match(lastComment, /^# (.*)/); \
	    helpCommand = $$1; sub(/:$$/, "", helpCommand); \
	    if (helpMessage) { \
	        printf "  \033[1;32m%-20s\033[0m \033[0;37m%s\033[0m\n", helpCommand, substr(lastComment, RSTART + 2, RLENGTH - 2); \
	    } else { \
	        printf "  \033[1;32m%-20s\033[0m \033[0;33m??? [No description]\033[0m\n", helpCommand; \
	    } \
	    lastComment = ""; \
	} \
	/^# / { \
	    lastComment = $$0; \
	} \
	/^\.PHONY:/ { \
	    next; \
	}' $(MAKEFILE_LIST) | sort
	@echo ""


# Setup the development environment
.PHONY: setup-dev-env
setup-dev-env: update install lint
	@echo "🚀 Setting up Git hooks..."
	poetry run pre-commit install
	@if [ -f .git/hooks/pre-commit ]; then chmod +x .git/hooks/pre-commit; fi
	@echo "✅ Development environment is ready!"


# Sync dependencies, updating poetry.lock and .venv
.PHONY: update
update:
	poetry update


# Install dependencies from poetry.lock
.PHONY: install
install:
	poetry install


# List all outdated dependencies (direct dependencies only)
.PHONY: outdated
outdated:
	poetry show --outdated --top-level


# List all outdated dependencies (including transitive dependencies)
.PHONY: outdated-all
outdated-all:
	poetry show --outdated


# Lint all files (fails on errors)
.PHONY: lint
lint:
	@echo "🔍 Running Ruff..."
	@poetry run ruff check . || lint_failed=1
	@echo "🔍 Running Pyright..."
	@poetry run pyright . || lint_failed=1
	@echo "🔍 Running Mypy..."
	@poetry run mypy . || lint_failed=1
	@exit $${lint_failed:-0}


# Run tests
.PHONY: test
test:
	poetry run pytest --maxfail=1 --disable-warnings


# Run test coverage (with 80% minimum threshold)
.PHONY: coverage
coverage:
	poetry run pytest --cov=. --cov-report=term-missing --cov-fail-under=80


# Run the application
.PHONY: run
run:
	@echo "🚀 Running the application..."
	poetry run python -m blogscraper.main


# Debug the application with PDB
.PHONY: debug
debug:
	@echo "🐞 Running the application in debug mode..."
	poetry run python -m pdb -m blogscraper.main
````

## File: pyproject.toml
````toml
[project]
name = "blogscraper"
version = "0.1.0"
description = ""
authors = [
    {name = "David Goldfarb",email = "deg@degel.com"}
]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
]


[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.group.dev.dependencies]
mypy = "1.15.0"
pre-commit = "4.1.0"
pyright = "1.1.395"
pytest = "8.3.4"
pytest-cov = "6.0.0"
ruff = "0.9.8"
black = "25.1.0"
ipython = "8.32.0"


[tool.poetry.scripts]
blogscraper = "src.blogscraper.main:main"

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203"]

[tool.mypy]
strict = true

[tool.pytest]
minversion = "6.0"
addopts = "-ra -q --cov=."
testpaths = ["tests"]
````

## File: README.md
````markdown
# blogscraper
````

## File: spec.md
````markdown
# Blog Post URL Scraper - Developer Specification

## Overview
This project is a **lightweight scraper** designed to collect **blog post URLs** from a small set of manually selected blogs. The goal is to **gather links to full posts**, which can then be processed by an external tool like **Notebook LM** for querying and analysis.

## Key Features
- **Manual invocation**: The scraper runs only when executed.
- **Custom scraping logic per blog**: Each blog has a dedicated function for extracting post URLs.
- **Optional one-level-deep link extraction**: Per-blog configurable logic to collect certain links found inside posts.
- **Deduplication**: Previously collected URLs are stored to prevent re-scraping.
- **JSON-based storage**: URLs and metadata are saved in a simple file format.
- **Basic testing framework**: Lightweight tests to validate scraper functionality.

---
## Architecture & Implementation

### **Project Structure**
```
project_root/
  ├── Makefile
  ├── pyproject.toml
  ├── README.md
  ├── src/
  │   ├── main.py        # Entry point for scraping
  │   ├── scrapers/      # Site-specific scrapers
  │   │   ├── thezvi.py
  │   │   ├── simonwillison.py
  │   ├── utils.py       # Shared utilities (if needed)
  ├── data/
  │   ├── urls.json      # Collected URLs
  │   ├── errors.log     # Error logs (if needed)
  ├── tests/
  │   ├── test_scrapers.py  # Unit tests for site-specific scrapers
```

### **Technology Stack**
- **Python** 3.11+
- **Requests + BeautifulSoup** for web scraping
- **JSON storage** for tracking collected URLs
- **Pytest** for basic test coverage

---
## Data Handling

### **Collected Data Format (`urls.json`)**
```json
[
  {
    "url": "https://thezvi.wordpress.com/2025/02/26/welcome-claude-3-7",
    "timestamp": "2025-02-26T12:00:00",
    "source": "thezvi"
  },
  {
    "url": "https://simonwillison.net/2025/02/26/some-post/",
    "timestamp": "2025-02-26T12:05:00",
    "source": "simonwillison"
  }
]
```
- Each entry represents a **unique** blog post.
- **Timestamps** store when a URL was collected.
- Additional metadata (e.g., titles, tags) can be added later as needed.

### **Duplicate Handling**
- **Skip previously collected URLs** by checking against `urls.json`.
- **No versioning**—once a URL is collected, it's assumed correct.

---
## Scraping Logic

### **Site-Specific Scraping**
Each blog has its own scraper function inside `src/scrapers/`. These functions:
1. **Navigate blog archives** (e.g., monthly archives, "Older Posts" pagination).
2. **Extract post URLs** using CSS selectors or other methods.
3. **Return a list of URLs** for saving.

Example:
```python
from bs4 import BeautifulSoup
import requests

def scrape_thezvi():
    root_url = "https://thezvi.wordpress.com/"
    archive_urls = generate_archive_links(root_url)  # Custom per-site logic
    post_urls = []
    
    for url in archive_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        post_links = soup.select("article h2 a")  # Example selector
        post_urls.extend(link["href"] for link in post_links)
    
    return post_urls
```

### **Handling Pagination & Archives**
- **Custom per-blog logic** to find archive pages (e.g., `/YYYY/MM/`, `/page/2/`).
- **Manual configuration** for each blog since archive structures vary.
- **Support functions** in `utils.py` for common patterns (e.g., generating archive URLs).

### **One-Level-Deep Link Extraction**
- Per-blog **optional setting** to follow links **within blog post bodies**.
- A simple heuristic can detect **contextually relevant** links (e.g., not navigation links).
- Can be manually configured per site.

---
## Execution & Error Handling

### **Running the Scraper**
- Command-line execution:
  ```bash
  python src/main.py
  ```
- Runs for **all configured blogs** (no arguments needed yet).

### **Error Handling**
- **Fail fast**: If a request fails, print the error and stop execution.
- **No retries yet** (can be added later).
- **Console logging only** for now (logs can be added later if needed).

---
## Testing Plan

### **Basic Unit Tests** (in `tests/test_scrapers.py`)
- Ensure `scrape_thezvi()` and other functions return **valid URL lists**.
- Example:
  ```python
  from src.scrapers.thezvi import scrape_thezvi
  
  def test_scrape_thezvi():
      urls = scrape_thezvi()
      assert isinstance(urls, list)
      assert all(url.startswith("https://thezvi.wordpress.com/") for url in urls)
  ```

### **Manual Test Mode**
- Run with `--test` flag to print URLs instead of saving:
  ```bash
  python src/main.py --test
  ```
- Allows quick debugging without modifying `urls.json`.

---
## Future Enhancements
- **Retry logic for failed requests.**
- **Configurable delays to avoid rate limiting.**
- **Logging system for error tracking.**
- **Filtering/heuristics for smarter link following.**
- **Exporting URLs in Notebook LM-friendly formats.**

---
## Summary
This scraper is designed for **simplicity and flexibility**, enabling quick collection of blog post URLs while keeping logic **customizable per site**. The current implementation **focuses on core functionality**, with room for future improvements as needed.

With this spec, a developer should be able to **immediately start building the scraper** and iterating based on real-world performance.
````
