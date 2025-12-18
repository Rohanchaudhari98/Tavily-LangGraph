from tavily import TavilyClient
from app.config import settings
from app.utils.env import require_env


def get_tavily_client() -> TavilyClient:
    require_env("TAVILY_API_KEY", settings.tavily_api_key)

    return TavilyClient(api_key=settings.tavily_api_key)
