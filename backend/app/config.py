from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration"""

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "stock_news"

    # Zhipu AI
    zhipu_api_key: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: List[str] = ["*"]

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

