"""Application configuration management."""
import os
import logging
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./reflx.db")

    # Admin defaults
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")

    # Application
    APP_ENV: Literal["development", "production"] = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Cache & Offline
    ENABLE_OFFLINE_MODE: bool = os.getenv("ENABLE_OFFLINE_MODE", "true").lower() == "true"
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "50"))
    SYNC_RETRY_ATTEMPTS: int = int(os.getenv("SYNC_RETRY_ATTEMPTS", "3"))
    SYNC_RETRY_DELAY: int = int(os.getenv("SYNC_RETRY_DELAY", "2"))  # seconds

    @property
    def is_sqlite(self) -> bool:
        """Check if database is SQLite."""
        return "sqlite" in self.DATABASE_URL

    @property
    def connect_args(self) -> dict:
        """Get database connection arguments."""
        return {"check_same_thread": False} if self.is_sqlite else {}

    def setup_logging(self):
        """Configure application logging."""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log') if self.APP_ENV == 'production' else logging.NullHandler()
            ]
        )


config = Config()
config.setup_logging()
