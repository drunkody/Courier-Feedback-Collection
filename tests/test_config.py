"""Tests for application configuration."""
import pytest
import os
from app.enums import AppMode
from config import Config


@pytest.mark.unit
class TestConfig:
    """Tests for the Config class."""

    def test_traditional_mode_configuration(self):
        """Test configuration for traditional mode."""
        # Create a fresh config instance
        config = Config()
        config.APP_MODE = "traditional"
        config._configure_mode()
        
        assert config.mode == AppMode.TRADITIONAL
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is False
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is False
        assert config.requires_backend is True
        assert config.requires_jazz is False

    def test_jazz_only_mode_configuration(self):
        """Test configuration for jazz_only mode."""
        config = Config()
        config.APP_MODE = "jazz_only"
        config._configure_mode()
        
        assert config.mode == AppMode.JAZZ_ONLY
        assert config.USE_BACKEND is False
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is True
        assert config.OFFLINE_FIRST is True
        assert config.requires_backend is False
        assert config.requires_jazz is True

    def test_hybrid_mode_configuration(self):
        """Test configuration for hybrid mode."""
        config = Config()
        config.APP_MODE = "hybrid"
        config._configure_mode()
        
        assert config.mode == AppMode.HYBRID
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is False
        assert config.requires_backend is True
        assert config.requires_jazz is True

    def test_offline_first_mode_configuration(self):
        """Test configuration for offline_first mode."""
        config = Config()
        config.APP_MODE = "offline_first"
        config._configure_mode()
        
        assert config.mode == AppMode.OFFLINE_FIRST
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is True
        assert config.requires_backend is True
        assert config.requires_jazz is True

    def test_invalid_mode_raises_error(self):
        """Test that an invalid APP_MODE raises a ValueError."""
        config = Config()
        config.APP_MODE = "invalid_mode"
        
        with pytest.raises(ValueError, match="Invalid APP_MODE"):
            config._configure_mode()

    def test_is_sqlite_property(self):
        """Test is_sqlite property detection."""
        config = Config()
        config.DATABASE_URL = "sqlite:///test.db"
        assert config.is_sqlite is True

    def test_is_postgres_property(self):
        """Test is_sqlite property with PostgreSQL."""
        config = Config()
        config.DATABASE_URL = "postgresql://user:pass@localhost/db"
        assert config.is_sqlite is False

    def test_connect_args_for_sqlite(self):
        """Test connect_args for SQLite."""
        config = Config()
        config.DATABASE_URL = "sqlite:///test.db"
        assert "check_same_thread" in config.connect_args
        assert config.connect_args["check_same_thread"] is False

    def test_connect_args_for_postgres(self):
        """Test connect_args for PostgreSQL."""
        config = Config()
        config.DATABASE_URL = "postgresql://user:pass@localhost/db"
        assert config.connect_args == {}

