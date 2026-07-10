import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings:
    app_name: str = "Personal Email Agent"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    gmail_credentials_path: str = os.getenv(
        "GMAIL_CREDENTIALS_PATH",
        str(BACKEND_DIR / "credentials.json"),
    )
    gmail_token_path: str = os.getenv(
        "GMAIL_TOKEN_PATH",
        str(BACKEND_DIR / "token.json"),
    )
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    analysis_provider: str = os.getenv("ANALYSIS_PROVIDER", "rule_based")
    # Comma-separated extra origins allowed by CORS (e.g. deployed frontend URL)
    cors_extra_origins: str = os.getenv("CORS_EXTRA_ORIGINS", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
