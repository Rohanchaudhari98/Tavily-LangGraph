def require_env(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set")
