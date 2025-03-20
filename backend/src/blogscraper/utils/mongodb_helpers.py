# - from datetime import datetime

from dataclasses import asdict
from datetime import datetime
from typing import Any, cast

from bson import ObjectId
from dacite import from_dict
from degel_python_utils import setup_logger

# - from pydantic import BaseModel, HttpUrl
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from blogscraper.types import URLDict

BlogDBClient = MongoClient[dict[str, object]]
BlogDatabase = Database[dict[str, object]]
BlogCollection = Collection[dict[str, object]]

logger = setup_logger(__name__)
# pylint: disable=logging-format-interpolation


# - class BlogPost(BaseModel):
# -     url: HttpUrl
# -     source: str
# -     content: str
# -     creation_timestamp: datetime
# -     harvest_timestamp: datetime
BlogPost = URLDict

PostCollection = Collection[dict[str, object]]


# Global variables for database and collections
_db: BlogDatabase | None = None
_collections: dict[str, BlogCollection] = {}


def the_db() -> BlogDatabase | None:
    return _db


def init_db() -> None:
    """
    Initializes a connection to the local MongoDB instance and initializes global
    state variables.

    Returns:
        tuple[Database, Collection]: The database instance and "blog_posts" collection.
    """
    global _db, _collections

    client: BlogDBClient = MongoClient("mongodb://blo_db:27017")
    db = client["blogscraper"]

    posts_coll = db["blog_posts"]
    posts_coll.create_index("url", unique=True)
    posts_coll.create_index("clean_url", unique=True)

    _db = db
    _collections = {"posts": posts_coll}


def close_db() -> None:
    global _db, _collections
    if _db is not None:
        _db.client.close()
        logger.info("MongoDB connection closed")
    _db = None
    _collections = {}


def get_posts_collection() -> PostCollection:
    return cast(PostCollection, _get_collection("posts"))


def _get_collection(name: str) -> BlogCollection:
    """Dependency to provide a specific MongoDB collection."""
    if name not in _collections:
        raise ValueError(f"Collection {name} does not exist")
    return _collections[name]


def add_post(url_dict: URLDict) -> ObjectId | None:
    posts_coll = get_posts_collection()
    try:
        result = posts_coll.insert_one(asdict(url_dict))
        logger.info(f"✅ Inserted post {url_dict.url}")
        return cast(ObjectId, result.inserted_id)
    except DuplicateKeyError:
        logger.info(f"⚠️ URL already in database: {url_dict.url}")
    except Exception as e:
        logger.error(f"⚠️ Failed to insert URL: {e}")
    return None


def post_sources(roots_only: bool = False) -> list[str]:
    """
    Retrieve a unique list of all sources from the posts collection.

    Parameters:
    - roots_only: If True, only include scrapers, not ref sources

    Returns:
    - list[str]: A sorted list of unique source names.
    """
    sources = get_posts_collection().distinct("source")
    if roots_only:
        sources = [s for s in sources if not s.lower().startswith("http")]
    return sorted(sources)


def get_documents(doc_ids: list[ObjectId]) -> list[URLDict]:
    posts_coll = get_posts_collection()
    raw_documents = list(posts_coll.find({"_id": {"$in": doc_ids}}, {"_id": 0}))
    return list([from_dict(URLDict, doc) for doc in raw_documents])


def filter_posts(
    start_dt: datetime | None = None,
    end_dt: datetime | None = None,
    source: str | None = None,
) -> list[URLDict]:
    """
    Retrieve posts from MongoDB based on optional filters.

    Parameters:
    - start_dt: Earliest `creation_date` (inclusive).
    - end_dt: Latest `creation_date` (inclusive).
    - source: Exact match for the `source` field (case-sensitive).

    Returns:
    - list[dict]: A list of matching posts, excluding `_id`.
    """
    posts_coll = get_posts_collection()
    query: dict[str, Any] = {}

    if start_dt:
        query.setdefault("creation_date", {})["$gte"] = start_dt
    if end_dt:
        query.setdefault("creation_date", {})["$lte"] = end_dt
    if source:
        query["source"] = source  # Exact case-sensitive match

    raw_documents = list(posts_coll.find(query, {"_id": 0}))
    return [from_dict(URLDict, doc) for doc in raw_documents]
