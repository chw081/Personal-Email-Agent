import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name: str = "Personal Email Agent"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()
