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
