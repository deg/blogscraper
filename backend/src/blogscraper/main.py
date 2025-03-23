"""Main entry point for the Blogscraper CLI.

Handles user interaction, scraper execution, and data processing.
Allows users to fetch recent blog posts, view their contents, and generate reports.

Usage:
    Run this module to start the Blogscraper CLI. Typically, start with `make run` The
    script guides users through interactive choices for scraping and processing data.

"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from degel_python_utils import appEnv, setup_logger
from fastapi import Depends, FastAPI, Query
from starlette.middleware.gzip import GZipMiddleware

from blogscraper.tasks import generate_doc, generate_llm_prompt, scrape_blogs
from blogscraper.types import FilterRangeQuery, GDoc
from blogscraper.utils.google_interface import (
    delete_service_account_doc,
    list_service_account_docs,
)
from blogscraper.utils.mongodb_helpers import (
    close_db,
    filter_posts,
    init_db,
    post_sources,
    the_db,
)

APP_NAME = "Blog Scraper"
APP_DESCRIPTION = "Summarize interesting recent AI blog posts"


logger = setup_logger(__name__)


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


@app.post("/scrape", tags=["Scrape"])
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
        await asyncio.to_thread(scrape_blogs, status_callback=status_callback)
        scrape_tasks[task_id] = "completed"
        logger.major("Scrape completed")
    except Exception as e:
        scrape_tasks[task_id] = f"failed: {str(e)}"
        logger.warning("Scrape failed")


@app.get("/scrape/status/{task_id}", tags=["Scrape"])
async def scrape_status(task_id: str) -> dict[str, str]:
    """Returns the status of a scraping task."""
    return {"task_id": task_id, "status": scrape_tasks.get(task_id, "not found")}


@app.get("/sources", response_model=list[str], tags=["Query"])
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


@app.get("/list-google-docs", response_model=list[GDoc], tags=["Google"])
async def list_google_docs() -> list[GDoc]:
    return list_service_account_docs()


@app.post("/delete-google-doc", response_model=bool, tags=["Google"])
async def delete_google_doc(doc_id: str, name: str) -> bool:
    return delete_service_account_doc(doc_id, name)


@app.get("/list-documents", response_model=list[str], tags=["Query"])
async def list_documents(query: FilterRangeQuery = Depends()) -> list[str]:
    # [TODO] Really should project just "url" in filter_posts, but that breaks the
    # from_dict return there.
    return [
        u.url
        for u in filter_posts(
            start_dt=query.start_dt,
            end_dt=query.end_dt,
            source=query.source,
            match_string=query.match_string,
        )
    ]


@app.get("/llm-prompt-from-documents", tags=["Query"])
async def llm_prompt_from_documents(query: FilterRangeQuery = Depends()) -> str:
    return generate_llm_prompt(query)


@app.get("/markdown-from-documents", tags=["Query"])
async def markdown_from_documents(query: FilterRangeQuery = Depends()) -> str:
    return generate_doc(query, format="Markdown")


@app.get("/google-doc-from-documents", tags=["Query"])
async def google_doc_from_documents(query: FilterRangeQuery = Depends()) -> str:
    return generate_doc(query, format="Google Doc")


# - if __name__ == "__main__":  # pragma: no cover
# -     try:
# -         main()
# -     except KeyboardInterrupt:
# -         print("\nAborted by user. Exiting...")
# -         sys.exit(1)
