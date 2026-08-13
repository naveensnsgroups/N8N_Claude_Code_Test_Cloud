"""
Configuration module for FastAPI application.
Handles environment variables and app settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB
    mongo_uri: str = os.getenv('MONGO_URI', 'mongodb://localhost:27017')

    # API Configuration
    api_title: str = "Personal Details API"
    api_version: str = "1.0.0"

    # Server
    host: str = os.getenv('HOST', '0.0.0.0')
    port: int = int(os.getenv('PORT', 5000))
    environment: str = Field(
        default='development',
        validation_alias='NODE_ENV',
    )

    # CORS
    client_url: str = os.getenv('CLIENT_URL', 'http://localhost:5173')

    # Rate limiting
    rate_limit_window_ms: int = 15 * 60 * 1000  # 15 minutes
    rate_limit_max_requests: int = 100

    class Config:
        env_file = '.env'
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
