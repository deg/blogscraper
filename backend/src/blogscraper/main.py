"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

import asyncio
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import AsyncIterator

from degel_python_utils import appEnv, setup_logger
from fastapi import Depends, FastAPI, HTTPException, Query
from starlette.middleware.gzip import GZipMiddleware

from blogscraper.tasks import generate_doc, scrape_blogs

# - from blogscraper.ui import confirm_action, console, display_welcome, warnstr
from blogscraper.utils.mongodb_helpers import (
    close_db,
    filter_posts,
    init_db,
    post_sources,
    the_db,
)

# -     delete_unneeded_docs,
# -     display_blogs,
# -     filter_urls_by_date_range,
# -     generate_llm_prompt,
# -     list_urls,
# -     scrape_blogs,


# - from blogscraper.utils.storage import load_stored_urls

APP_NAME = "Blog Scraper"
APP_DESCRIPTION = "Summarize interesting recent AI blog posts"


logger = setup_logger(__name__)
# pylint: disable=logging-fstring-interpolation


@asynccontextmanager
async def server_lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle setup and teardown of server."""
    appEnv.set_app_name(APP_NAME)
    appEnv.register_env_var("BACKEND_PORT")
    appEnv.register_env_var("MONGODB_PORT")
    appEnv.register_env_var("GOOGLE_SERVICE_ACCOUNT_FILE", private=True)
    appEnv.show_env()

    init_db()
    db = the_db()
    if db is None:
        logger.error("Failed to initialize MongoDB connection")
        logger.warning(f"⚠️ {APP_NAME} ready, but probably not stable")
    else:
        logger.info(f"Connected to MongoDB: {db.name}")
        logger.info(f"✅ {APP_NAME} ready")

    yield

    close_db()
    logger.major("🛑 Shut down server")


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


@app.get("/", tags=["API"])
def health() -> dict[str, str]:
    """Get server status"""
    return {"message": "Blogscraper is running"}


# Store task status
scrape_tasks: dict[str, str] = {}


@app.post("/scrape", tags=["API"])
async def start_scrape(
    # posts_coll: PostCollection = Depends(get_posts_collection),
) -> dict[str, str]:
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
        logger.major("Scrape completed")
    except Exception as e:
        scrape_tasks[task_id] = f"failed: {str(e)}"
        logger.warning("Scrape failed")


@app.get("/scrape/status/{task_id}", tags=["API"])
async def scrape_status(task_id: str) -> dict[str, str]:
    """Returns the status of a scraping task."""
    return {"task_id": task_id, "status": scrape_tasks.get(task_id, "not found")}


@app.get("/sources", response_model=list[str])
async def sources(
    roots_only: bool = Query(False, description="Return only root sources")
) -> list[str]:
    """
    Fetch a unique list of all sources in the collection.

    Parameters:
    - roots_only: If True, returns only root sources from `SCRAPERS`.
                  Otherwise, fetches distinct sources from the database.

    Returns:
    - list of unique source names.
    """
    return post_sources(roots_only=roots_only)


class FilterRangeQuery:
    """Query parameters for fetching documents within a date range."""

    def __init__(
        self,
        start_date: date = Query(..., description="Start date (inclusive)"),
        end_date: date = Query(..., description="End date (inclusive)"),
        source: str | None = Query(None, description="Filter by source"),
    ):
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="start_date must be before end_date."
            )
        self.start_date = start_date
        self.end_date = end_date
        self.source = source

    @property
    def start_dt(self) -> datetime:
        return datetime.combine(self.start_date, datetime.min.time())

    @property
    def end_dt(self) -> datetime:
        return datetime.combine(self.end_date, datetime.max.time())


@app.get("/list-documents", response_model=list[str])
async def list_documents(query: FilterRangeQuery = Depends()) -> list[str]:
    # [TODO] Really should project just "url" in filter_posts, but that breaks the
    # from_dict return there.
    return [
        u.url
        for u in filter_posts(
            start_dt=query.start_dt,
            end_dt=query.end_dt,
            source=query.source,
        )
    ]


@app.get("/markdown-from-documents")
async def markdown_from_documents(query: FilterRangeQuery = Depends()) -> str:
    urls = filter_posts(
        start_dt=query.start_dt, end_dt=query.end_dt, source=query.source
    )
    return generate_doc(urls, query.start_dt, query.end_dt, format="Markdown")


# - def main() -> None:
# -     """Starts the Blogscraper CLI and handles user interactions."""
# -     display_welcome()
# -
# -     all_urls = []
# -     if confirm_action("Scrape websites for new URLs?"):
# -         erase_old = confirm_action("Erase old DB and start fresh?", default=False)
# -         all_urls = scrape_blogs(do_all=False, erase_old=erase_old, posts_coll=None)
# -     else:
# -         all_urls = load_stored_urls()
# -
# -     ranged_urls, start_day, end_day = filter_urls_by_date_range(all_urls)
# -     if not ranged_urls:
# -         console.print(warnstr("No posts in the selected time period."))
# -         return
# -
# -     if confirm_action("Display contents of selected blogs?"):
# -         display_blogs(ranged_urls)
# -
# -     if confirm_action("Display a list of the URLs?"):
# -         list_urls(ranged_urls)
# -
# -     if confirm_action("Generate a consolidated Google Doc?"):
# -         generate_doc(ranged_urls, start_day, end_day, format="Google Doc")
# -
# -     if confirm_action("Generate a consolidated Markdown file?"):
# -         generate_doc(ranged_urls, start_day, end_day, format="Markdown")
# -
# -     if confirm_action("Generate an ad-hoc LLM prompt?"):
# -         generate_llm_prompt(ranged_urls)
# -
# -     delete_unneeded_docs()
# -
# -
# - if __name__ == "__main__":  # pragma: no cover
# -     try:
# -         main()
# -     except KeyboardInterrupt:
# -         print("\nAborted by user. Exiting...")
# -         sys.exit(1)
