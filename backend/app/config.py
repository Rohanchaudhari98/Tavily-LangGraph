from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    tavily_api_key: Optional[str]
    openai_api_key: Optional[str]
    mongodb_uri: Optional[str]
    mongodb_db_name: str = "competitive_intelligence"

    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8080

    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = []

    class Config:
        env_file = ".env"  # EB can override with environment variables
        case_sensitive = False
        env_prefix = ""

    # Convert comma-separated string to list
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.cors_origins, str):
            return [o.strip() for o in self.cors_origins.replace("[","").replace("]","").replace('"','').split(",")]
        return self.cors_origins

settings = Settings()
