"""
Configuration module for the Guardian API application.

This module handles application settings, database configuration, and Redis setup
using Pydantic settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        redis_host (str): Redis server host. Default: localhost
        redis_port (int): Redis server port. Default: 6379
        redis_db (int): Redis database number. Default: 0
        database_url (str): SQLAlchemy database URL. Default: sqlite:///./guardian.db
        testing (bool): Whether running in test mode. Default: False
    """
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    database_url: str = "sqlite:///./guardian.db"
    testing: bool = False

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()

# Override for testing
if os.getenv("TESTING") or settings.testing:
    settings.database_url = "postgresql://test:test@localhost:5432/test_db"

# SQLAlchemy setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()