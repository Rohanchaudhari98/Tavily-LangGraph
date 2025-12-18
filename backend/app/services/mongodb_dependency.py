from app.services.mongodb_service import MongoDBService
from app.config import settings
from app.utils.env import require_env

_db: MongoDBService | None = None

def get_db() -> MongoDBService:
    """Lazy MongoDBService getter for FastAPI dependencies."""
    global _db

    # Validate env var at runtime
    require_env("MONGODB_URI", settings.mongodb_uri)

    if _db is None:
        _db = MongoDBService(
            connection_string=settings.mongodb_uri,
            database_name=settings.mongodb_db_name
        )

    return _db
