"""Tests for application configuration."""
import pytest
import os
from app.enums import AppMode


@pytest.mark.unit
class TestConfig:
    """Tests for the Config class."""

    def test_default_mode_is_hybrid(self, monkeypatch):
        """Test that the default APP_MODE is hybrid."""
        monkeypatch.setenv("APP_MODE", "hybrid")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        from config import Config
        config = Config()
        
        assert config.APP_MODE == "hybrid"
        assert config.mode == AppMode.HYBRID
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is False

    def test_traditional_mode_configuration(self, monkeypatch):
        """Test configuration for traditional mode."""
        monkeypatch.setenv("APP_MODE", "traditional")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        from config import Config
        config = Config()
        
        assert config.mode == AppMode.TRADITIONAL
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is False
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is False
        assert config.requires_backend is True
        assert config.requires_jazz is False

    def test_jazz_only_mode_configuration(self, monkeypatch):
        """Test configuration for jazz_only mode."""
        monkeypatch.setenv("APP_MODE", "jazz_only")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        from config import Config
        config = Config()
        
        assert config.mode == AppMode.JAZZ_ONLY
        assert config.USE_BACKEND is False
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is True
        assert config.OFFLINE_FIRST is True
        assert config.requires_backend is False
        assert config.requires_jazz is True

    def test_hybrid_mode_configuration(self, monkeypatch):
        """Test configuration for hybrid mode."""
        monkeypatch.setenv("APP_MODE", "hybrid")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        from config import Config
        config = Config()
        
        assert config.mode == AppMode.HYBRID
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is False
        assert config.requires_backend is True
        assert config.requires_jazz is True

    def test_offline_first_mode_configuration(self, monkeypatch):
        """Test configuration for offline_first mode."""
        monkeypatch.setenv("APP_MODE", "offline_first")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        from config import Config
        config = Config()
        
        assert config.mode == AppMode.OFFLINE_FIRST
        assert config.USE_BACKEND is True
        assert config.USE_JAZZ_SYNC is True
        assert config.JAZZ_ONLY_MODE is False
        assert config.OFFLINE_FIRST is True
        assert config.requires_backend is True
        assert config.requires_jazz is True

    def test_invalid_mode_raises_error(self, monkeypatch):
        """Test that an invalid APP_MODE raises a ValueError."""
        monkeypatch.setenv("APP_MODE", "invalid_mode")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        
        with pytest.raises(ValueError, match="Invalid APP_MODE"):
            from config import Config
            Config()

    def test_is_sqlite_property(self, monkeypatch):
        """Test is_sqlite property detection."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        monkeypatch.setenv("APP_MODE", "traditional")
        
        from config import Config
        config = Config()
        assert config.is_sqlite is True

    def test_is_postgres_property(self, monkeypatch):
        """Test is_sqlite property with PostgreSQL."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("APP_MODE", "traditional")
        
        from config import Config
        config = Config()
        assert config.is_sqlite is False

    def test_connect_args_for_sqlite(self, monkeypatch):
        """Test connect_args for SQLite."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        monkeypatch.setenv("APP_MODE", "traditional")
        
        from config import Config
        config = Config()
        assert "check_same_thread" in config.connect_args
        assert config.connect_args["check_same_thread"] is False

    def test_connect_args_for_postgres(self, monkeypatch):
        """Test connect_args for PostgreSQL."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("APP_MODE", "traditional")
        
        from config import Config
        config = Config()
        assert config.connect_args == {}

