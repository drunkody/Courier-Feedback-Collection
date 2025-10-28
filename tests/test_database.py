"""Tests for database functions."""
from sqlmodel import Session, select
from app.database import (
    _seed_default_admin,
    _seed_sample_courier,
    AdminUser,
    Courier,
    engine,
)


def test_seed_default_admin(db_session):
    """Test that the default admin is created."""
    _seed_default_admin()
    with Session(engine) as session:
        admin = session.exec(select(AdminUser)).first()
        assert admin is not None
        assert admin.username == "admin"


def test_seed_sample_courier(db_session):
    """Test that the sample courier is created."""
    _seed_sample_courier()
    with Session(engine) as session:
        courier = session.exec(select(Courier).where(Courier.id == 123)).first()
        assert courier is not None
        assert courier.name == "Alex Doe"
