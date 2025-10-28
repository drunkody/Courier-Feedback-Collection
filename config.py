"""Application configuration management."""
import os
import logging
from typing import Literal
from dotenv import load_dotenv
from app.enums import AppMode

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

    # Deployment Mode
    APP_MODE: str = os.getenv("APP_MODE", "hybrid")  # traditional, jazz_only, hybrid, offline_first

    # Cache & Offline
    ENABLE_OFFLINE_MODE: bool = os.getenv("ENABLE_OFFLINE_MODE", "true").lower() == "true"
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "50"))
    SYNC_RETRY_ATTEMPTS: int = int(os.getenv("SYNC_RETRY_ATTEMPTS", "3"))
    SYNC_RETRY_DELAY: int = int(os.getenv("SYNC_RETRY_DELAY", "2"))  # seconds

    # Jazz Configuration
    JAZZ_SYNC_SERVER: str = os.getenv("JAZZ_SYNC_SERVER", "wss://cloud.jazz.tools")
    JAZZ_ENABLE_P2P: bool = os.getenv("JAZZ_ENABLE_P2P", "true").lower() == "true"
    JAZZ_AUTH_PROVIDER: str = os.getenv("JAZZ_AUTH_PROVIDER", "anonymous")
    JAZZ_STORAGE_ENCRYPTION: bool = os.getenv("JAZZ_STORAGE_ENCRYPTION", "true").lower() == "true"

    # Feature Flags (auto-configured based on mode)
    USE_BACKEND: bool = True
    USE_JAZZ_SYNC: bool = False
    JAZZ_ONLY_MODE: bool = False
    OFFLINE_FIRST: bool = False

    def __init__(self):
        """Initialize and configure based on APP_MODE."""
        self._configure_mode()

    def _configure_mode(self):
        """Auto-configure feature flags based on APP_MODE."""
        mode = self.APP_MODE.lower()

        if mode == "traditional":
            self.USE_BACKEND = True
            self.USE_JAZZ_SYNC = False
            self.JAZZ_ONLY_MODE = False
            self.OFFLINE_FIRST = False

        elif mode == "jazz_only":
            self.USE_BACKEND = False
            self.USE_JAZZ_SYNC = True
            self.JAZZ_ONLY_MODE = True
            self.OFFLINE_FIRST = True
            self.ENABLE_OFFLINE_MODE = True

        elif mode == "hybrid":
            self.USE_BACKEND = True
            self.USE_JAZZ_SYNC = True
            self.JAZZ_ONLY_MODE = False
            self.OFFLINE_FIRST = False

        elif mode == "offline_first":
            self.USE_BACKEND = True  # Optional fallback
            self.USE_JAZZ_SYNC = True
            self.JAZZ_ONLY_MODE = False
            self.OFFLINE_FIRST = True
            self.ENABLE_OFFLINE_MODE = True

        else:
            raise ValueError(f"Invalid APP_MODE: {mode}. Use: traditional, jazz_only, hybrid, or offline_first")

    @property
    def mode(self) -> AppMode:
        """Get current application mode."""
        return AppMode(self.APP_MODE.lower())

    @property
    def requires_backend(self) -> bool:
        """Check if backend is required."""
        return self.USE_BACKEND and not self.JAZZ_ONLY_MODE

    @property
    def requires_jazz(self) -> bool:
        """Check if Jazz is required."""
        return self.USE_JAZZ_SYNC or self.JAZZ_ONLY_MODE

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
        log_format = f'[{self.APP_MODE.upper()}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log') if self.APP_ENV == 'production' else logging.NullHandler()
            ]
        )

        logger = logging.getLogger(__name__)
        logger.info(f"🚀 App Mode: {self.APP_MODE.upper()}")
        logger.info(f"   Backend: {'✅' if self.USE_BACKEND else '❌'}")
        logger.info(f"   Jazz Sync: {'✅' if self.USE_JAZZ_SYNC else '❌'}")
        logger.info(f"   Jazz-Only: {'✅' if self.JAZZ_ONLY_MODE else '❌'}")
        logger.info(f"   Offline-First: {'✅' if self.OFFLINE_FIRST else '❌'}")


config = Config()
config.setup_logging()
