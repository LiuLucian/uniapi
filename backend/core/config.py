"""
Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "UniAPI"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend dev
        "http://localhost:8000",  # Backend dev
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://uniapi:uniapi@localhost:5432/uniapi"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Playwright
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000

    # Storage
    BROWSER_DATA_DIR: str = "./data/browser_profiles"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not defined in Settings


settings = Settings()
