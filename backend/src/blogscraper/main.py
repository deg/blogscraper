"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from degel_python_utils import appEnv, setup_logger
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

from blogscraper.tasks import (
    delete_unneeded_docs,
    display_blogs,
    filter_urls_by_date_range,
    generate_doc,
    generate_llm_prompt,
    list_urls,
    scrape_blogs,
)
from blogscraper.ui import confirm_action, console, display_welcome, warnstr
from blogscraper.utils.storage import load_stored_urls

APP_NAME = "Blog Scraper"
APP_DESCRIPTION = "Summarize interesting recent AI blog posts"

logger = setup_logger(__name__)
# pylint: disable=logging-fstring-interpolation


@asynccontextmanager
async def server_lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle setup and teardown of server."""
    appEnv.set_app_name(APP_NAME)
    appEnv.register_env_var("GOOGLE_SERVICE_ACCOUNT_FILE", private=True)
    appEnv.show_env()
    logger.info(f"{APP_NAME} ready")

    yield

    logger.major("Shut down server")


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0",
    lifespan=server_lifespan,
    openapi_tags=[
        {"name": "API", "description": "Catch-all for now"},
    ],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Store task status
scrape_tasks: dict[str, str] = {}


@app.post("/scrape")
async def start_scrape() -> dict[str, str]:
    """Starts scraping in an async background task."""
    task_id = str(len(scrape_tasks) + 1)
    scrape_tasks[task_id] = "queued"

    asyncio.create_task(_run_scrape(task_id))

    return {"task_id": task_id, "status": "started"}


async def _run_scrape(task_id: str) -> None:
    """Runs scrape_blogs(False) asynchronously and updates task status."""
    scrape_tasks[task_id] = "running"

    def status_callback(status: str) -> None:
        """Updates task status with intermediate progress."""
        scrape_tasks[task_id] = f"running: {status}"

    try:
        await asyncio.to_thread(
            scrape_blogs,
            do_all=True,
            erase_old=False,
            status_callback=status_callback,
        )
        scrape_tasks[task_id] = "completed"
    except Exception as e:
        scrape_tasks[task_id] = f"failed: {str(e)}"


@app.get("/scrape/status/{task_id}")
async def get_scrape_status(task_id: str) -> dict[str, str]:
    """Returns the status of a scraping task."""
    return {"task_id": task_id, "status": scrape_tasks.get(task_id, "not found")}


def main() -> None:
    """Starts the Blogscraper CLI and handles user interactions."""
    display_welcome()

    all_urls = []
    if confirm_action("Scrape websites for new URLs?"):
        erase_old = confirm_action("Erase old DB and start fresh?", default=False)
        all_urls = scrape_blogs(do_all=False, erase_old=erase_old)
    else:
        all_urls = load_stored_urls()

    ranged_urls, start_day, end_day = filter_urls_by_date_range(all_urls)
    if not ranged_urls:
        console.print(warnstr("No posts in the selected time period."))
        return

    if confirm_action("Display contents of selected blogs?"):
        display_blogs(ranged_urls)

    if confirm_action("Display a list of the URLs?"):
        list_urls(ranged_urls)

    if confirm_action("Generate a consolidated Google Doc?"):
        generate_doc(ranged_urls, start_day, end_day, format="Google Doc")

    if confirm_action("Generate a consolidated Markdown file?"):
        generate_doc(ranged_urls, start_day, end_day, format="Markdown")

    if confirm_action("Generate an ad-hoc LLM prompt?"):
        generate_llm_prompt(ranged_urls)

    delete_unneeded_docs()


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user. Exiting...")
        sys.exit(1)
