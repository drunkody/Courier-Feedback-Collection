"""Tests for database functions."""
import pytest
from sqlmodel import Session, select
from app.database import (
    AdminUser,
    Courier,
    hash_password,
    verify_password,
)


@pytest.mark.database
@pytest.mark.unit
class TestDatabaseSeeding:
    """Tests for database seeding functions."""

    def test_seed_default_admin(self, db_engine):
        """Test that the default admin is created."""
        from app.database import _seed_default_admin
        import app.database

        # Temporarily replace engine
        original_engine = app.database.engine
        app.database.engine = db_engine

        try:
            _seed_default_admin()

            with Session(db_engine) as session:
                admin = session.exec(
                    select(AdminUser).where(AdminUser.username == "admin")
                ).first()
                assert admin is not None
                assert admin.username == "admin"
                assert verify_password("admin", admin.password_hash)
        finally:
            app.database.engine = original_engine

    def test_seed_sample_courier(self, db_engine):
        """Test that the sample courier is created."""
        from app.database import _seed_sample_courier
        import app.database

        # Temporarily replace engine
        original_engine = app.database.engine
        app.database.engine = db_engine

        try:
            _seed_sample_courier()

            with Session(db_engine) as session:
                courier = session.exec(
                    select(Courier).where(Courier.id == 123)
                ).first()
                assert courier is not None
                assert courier.name == "Alex Doe"
                assert courier.phone == "+1-800-555-0101"
        finally:
            app.database.engine = original_engine


@pytest.mark.unit
class TestPasswordFunctions:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix
        assert len(hashed) == 60  # bcrypt hash length

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        result = verify_password("password", "invalid_hash")
        assert result is False
