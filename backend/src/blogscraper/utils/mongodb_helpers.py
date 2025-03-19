from datetime import datetime

from pydantic import BaseModel, HttpUrl
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

BlogDBClient = MongoClient[dict[str, object]]
BlogDatabase = Database[dict[str, object]]
BlogCollection = Collection[dict[str, object]]


class BlogPost(BaseModel):
    url: HttpUrl
    source: str
    content: str
    creation_timestamp: datetime
    harvest_timestamp: datetime


PostCollection = Collection[dict[str, BlogPost]]


def init_db() -> tuple[dict[str, BlogCollection], BlogDatabase]:
    """
    Initializes a connection to the local MongoDB instance and returns
    the database and the "blog_posts" collection.

    Returns:
        tuple[Database, Collection]: The database instance and "blog_posts" collection.
    """
    client: BlogDBClient = MongoClient("mongodb://localhost:27017")
    db = client["blogscraper"]
    collection = db["blog_posts"]

    return {"posts": collection}, db
