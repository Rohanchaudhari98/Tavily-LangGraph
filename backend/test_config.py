"""
Test that configuration loads correctly.
"""

import pytest
from app.config import settings


def test_config_loads():
    """Test that configuration loads correctly"""
    print("\n" + "="*70)
    print("CONFIGURATION TEST")
    print("="*70)

    assert settings.tavily_api_key, "Tavily API key not set"
    assert settings.openai_api_key, "OpenAI API key not set"
    assert settings.mongodb_uri, "MongoDB URI not set"
    assert settings.mongodb_db_name, "MongoDB DB name not set"

    print(f"\nTavily API Key: {settings.tavily_api_key[:20]}...")
    print(f"OpenAI API Key: {settings.openai_api_key[:20]}...")
    print(f"MongoDB URI: {settings.mongodb_uri[:40]}...")
    print(f"MongoDB DB Name: {settings.mongodb_db_name}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"API Host: {settings.api_host}")
    print(f"API Port: {settings.api_port}")
    print(f"Frontend URL: {settings.frontend_url}")
    print(f"CORS Origins: {settings.cors_origins}")

    print("\n" + "="*70)
    print("Config loaded successfully!")
    print("="*70 + "\n")