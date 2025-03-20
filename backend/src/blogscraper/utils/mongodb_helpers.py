# - from datetime import datetime

from dataclasses import asdict
from typing import cast

from bson import ObjectId
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
