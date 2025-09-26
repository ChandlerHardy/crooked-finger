from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://username:password@localhost/crypto_portfolio_db"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days (7 * 24 * 60)
    
    # External API Keys
    coinmarketcap_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    github_token: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000"

    # Admin secret for creating admin users
    admin_secret: str = "local-admin-secret"

    class Config:
        env_file = ".env"

settings = Settings()