from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    database_url: str = "sqlite:///./crooked_finger.db"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # External API Keys
    gemini_api_key: Optional[str] = None

    # Environment
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Admin secret for creating admin users
    admin_secret: str = "local-admin-secret"

    class Config:
        # Find .env file relative to this config.py file
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        extra = "ignore"
        case_sensitive = False  # Allow CORS_ORIGINS to map to cors_origins

settings = Settings()