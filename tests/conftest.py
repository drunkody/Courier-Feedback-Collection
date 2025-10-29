"""Shared test fixtures and configuration."""
import pytest
import os
import tempfile
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient

# Set test environment BEFORE any app imports
os.environ["APP_ENV"] = "testing"
os.environ["APP_MODE"] = "traditional"
os.environ["DATABASE_URL"] = "sqlite:///test.db"

from app.database import Courier, Feedback, AdminUser, hash_password
from config import Config


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    # Create temporary test database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    class TestConfig(Config):
        DATABASE_URL = f"sqlite:///{db_path}"
        APP_ENV = "testing"
        ENABLE_OFFLINE_MODE = True
        MAX_QUEUE_SIZE = 10
        SYNC_RETRY_ATTEMPTS = 2
        SYNC_RETRY_DELAY = 1
        APP_MODE = "traditional"

    config = TestConfig()

    yield config

    # Cleanup
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture(scope="function")
def db_engine(test_config):
    """Create test database engine."""
    engine = create_engine(
        test_config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # FIXED: Disable SQL echo in tests
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    with Session(db_engine) as session:
        yield session
        session.rollback()  # FIXED: Rollback after each test


@pytest.fixture
def sample_courier(db_session) -> Courier:
    """Create sample courier."""
    courier = Courier(
        id=1,
        name="Test Courier",
        phone="+1-555-0100",
        contact_link="https://example.com/courier"
    )
    db_session.add(courier)
    db_session.commit()
    db_session.refresh(courier)
    return courier


@pytest.fixture
def sample_admin(db_session) -> AdminUser:
    """Create sample admin user."""
    admin = AdminUser(
        username="testadmin",
        password_hash=hash_password("testpass123")
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def sample_feedback(db_session, sample_courier) -> Feedback:
    """Create sample feedback."""
    import json
    feedback = Feedback(
        order_id="TEST001",
        courier_id=sample_courier.id,
        rating=5,
        comment="Great service!",
        reasons=json.dumps(["Punctuality", "Politeness"]),
        publish_consent=True,
        needs_follow_up=False
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback


@pytest.fixture(scope="function")
def test_app(db_engine):
    """A test app that uses the test database."""
    # Import the FastAPI app (not the Reflex app)
    from app.app import api
    
    # Patch database engine for services
    import app.services
    original_service_engine = getattr(app.services, 'engine', None)
    app.services.engine = db_engine

    # Create tables
    SQLModel.metadata.create_all(db_engine)

    yield api

    # Restore
    if original_service_engine:
        app.services.engine = original_service_engine


@pytest.fixture
def api_client(test_app):
    """FastAPI test client."""
    return TestClient(test_app)


@pytest.fixture
def mock_feedback_data():
    """Mock feedback submission data."""
    return {
        "order_id": "TEST123",
        "courier_id": 1,
        "rating": 5,
        "comment": "Excellent delivery!",
        "reasons": ["Punctuality", "Politeness"],
        "publish_consent": True
    }


@pytest.fixture
def mock_invalid_feedback_data():
    """Mock invalid feedback data."""
    return {
        "order_id": "TEST456",
        "courier_id": 1,
        "rating": 6,  # Invalid rating
        "comment": "x" * 501,  # Too long
        "reasons": [],
        "publish_consent": False
    }


# FIXED: Remove autouse fixture that was causing issues
@pytest.fixture
def isolated_config(monkeypatch, test_config):
    """Provide isolated config for a test."""
    return test_config
