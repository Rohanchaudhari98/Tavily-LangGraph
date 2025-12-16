"""
Test that configuration loads correctly.
"""

from app.config import settings

print("\n" + "="*70)
print("CONFIGURATION TEST")
print("="*70)

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