from openai import OpenAI
from app.config import settings
from app.utils.env import require_env


def get_openai_client() -> OpenAI:
    require_env("OPENAI_API_KEY", settings.openai_api_key)

    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=120.0,  # 2 minute timeout for API calls
        max_retries=3  # Retry failed requests up to 3 times
    )
