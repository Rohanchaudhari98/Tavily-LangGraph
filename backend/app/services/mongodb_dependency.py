"""
MongoDB dependency for FastAPI.

Provides a singleton MongoDB service instance.
"""

from app.services.mongodb_service import MongoDBService
from app.config import settings
from app.utils.env import require_env

_db: MongoDBService | None = None


def get_db() -> MongoDBService:
    # Get MongoDB service instance for dependency injection
    global _db

    # Make sure we have the connection string
    require_env("MONGODB_URI", settings.mongodb_uri)

    if _db is None:
        _db = MongoDBService(
            connection_string=settings.mongodb_uri,
            database_name=settings.mongodb_db_name
        )

    return _db