"""Database models and initialization."""
import datetime
import logging
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
import bcrypt

from config import config

logger = logging.getLogger(__name__)

# Create engine with configuration
engine = create_engine(config.DATABASE_URL, connect_args=config.connect_args)


class Courier(SQLModel, table=True):
    """Courier model for delivery personnel."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: str
    contact_link: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Feedback(SQLModel, table=True):
    """Feedback model for delivery ratings."""

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    courier_id: int = Field(foreign_key="courier.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)
    reasons: str = Field(default="[]")  # JSON string
    publish_consent: bool = Field(default=False)
    needs_follow_up: bool = Field(default=False)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class AdminUser(SQLModel, table=True):
    """Admin user model for authentication."""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_db_and_tables():
    """Initialize database tables and seed default data."""
    SQLModel.metadata.create_all(engine)
    _seed_default_admin()
    _seed_sample_courier()


def _seed_default_admin():
    """Create default admin user if not exists."""
    with Session(engine) as session:
        # FIXED: Use SQLModel's exec() instead of query()
        statement = select(AdminUser).where(
            AdminUser.username == config.DEFAULT_ADMIN_USERNAME
        )
        admin = session.exec(statement).first()

        if not admin:
            logger.info("Creating default admin user...")
            admin = AdminUser(
                username=config.DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(config.DEFAULT_ADMIN_PASSWORD)
            )
            session.add(admin)
            session.commit()
            logger.info(f"Default admin created: {config.DEFAULT_ADMIN_USERNAME}")


def _seed_sample_courier():
    """Create sample courier for testing."""
    with Session(engine) as session:
        # FIXED: Use exec() with select() for consistency
        courier = session.get(Courier, 123)
        if not courier:
            logger.info("Creating sample courier...")
            courier = Courier(
                id=123,
                name="Alex Doe",
                phone="+1-800-555-0101",
                contact_link="https://t.me/alex_courier"
            )
            session.add(courier)
            session.commit()
            logger.info("Sample courier created (ID: 123)")
