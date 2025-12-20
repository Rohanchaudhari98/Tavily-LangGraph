"""
Application configuration.

Loads settings from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application settings loaded from environment variables
    
    # API Keys
    tavily_api_key: Optional[str]
    openai_api_key: Optional[str]
    
    # Database
    mongodb_uri: Optional[str]
    mongodb_db_name: str = "competitive_intelligence"

    # Environment
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8080

    # CORS
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string if needed."""
        if isinstance(self.cors_origins, str):
            return [o.strip() for o in self.cors_origins.replace("[","").replace("]","").replace('"','').split(",")]
        return self.cors_origins


settings = Settings()