"""
Configuration management using Pydantic Settings.
This loads environment variables and provides type-safe config access.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    tavily_api_key: str
    openai_api_key: str
    
    # MongoDB
    mongodb_uri: str
    mongodb_db_name: str = "competitive_intelligence"
    
    # App Config
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Config
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS - Allow frontend to connect
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()