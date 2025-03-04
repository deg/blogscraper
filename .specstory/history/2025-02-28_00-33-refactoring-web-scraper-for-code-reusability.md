## SpecStory

## Refactoring Web Scraper for Code Reusability (2/28/2025, 12:33:45 AM)

_**User**_

Write a similar scraper.  This time:
- The base_url is https://newsletter.cliffnotes.ai/
- This time (see attached) the <time> is within the <a>
- Try to share as much as code as possible between these two scrapers. (and, note, use the current code.  It has changed a lot after you wrote the original code earlier)

---

_**Assistant**_

To create a new scraper for the `https://newsletter.cliffnotes.ai/` site while reusing as much code as possible, we can refactor the existing code to make it more modular. We'll create a generic function to extract URLs and dates, which can be used by both scrapers.

Here's how you can refactor the code:

```python
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup, Tag
from blogscraper.types import URLDict
from blogscraper.utils.url_utils import normalize_url

def scrape_nathanbenaich() -> list[URLDict]:
    base_url = "https://nathanbenaich.substack.com/archive?sort=new"
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "div.portable-archive-list div", False)

def scrape_cliffnotes() -> list[URLDict]:
    base_url = "https://newsletter.cliffnotes.ai/"
    print(f"Fetching and parsing URLs from {base_url}")
    return scrape_blog(base_url, "a", True)

def scrape_blog(base_url: str, selector: str, time_within_a: bool) -> list[URLDict]:
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    archive_list = soup.select(selector)
    return extract_urls_from_archive(base_url, archive_list, time_within_a)

def extract_urls_from_archive(base_url: str, archive_list: list[Tag], time_within_a: bool) -> list[URLDict]:
    urls: list[URLDict] = []

    for entry in archive_list:
        link = entry if time_within_a else entry.find("a", href=True)
        time_tag = entry.find("time", datetime=True) if not time_within_a else entry

        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if not isinstance(href, str):
            continue
        if not isinstance(time_tag, Tag):
            continue

        creation_date_raw = time_tag.get("datetime")
        if not isinstance(creation_date_raw, str):
            continue

        absolute_url = normalize_url(base_url, href)
        creation_date = datetime.fromisoformat(creation_date_raw.replace("Z", "+00:00"))
        creation_date_str = creation_date.strftime("%Y-%m-%dT%H:%M:%S%z")

        url_dict: URLDict = {
            "url": absolute_url,
            "harvest_timestamp": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S%z"
            ),
            "source": base_url.split("//")[1].split("/")[0],
            "creation_date": creation_date_str,
        }
        urls.append(url_dict)

    return urls
```

### Explanation

1. **Modular Function**: The `scrape_blog` function is introduced to handle the common logic of fetching and parsing the HTML content. It takes a `selector` to identify the relevant HTML elements and a `time_within_a` flag to handle the different structures of the `<time>` tag.

2. **Shared Extraction Logic**: The `extract_urls_from_archive` function is modified to accommodate both scrapers by using the `time_within_a` flag to determine where to find the `<time>` tag.

3. **Dynamic Source**: The `source` field in the `URLDict` is dynamically set based on the base URL.

This setup allows you to easily add more scrapers in the future by simply calling `scrape_blog` with the appropriate parameters.

---



---

