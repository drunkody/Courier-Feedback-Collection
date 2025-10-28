import reflex as rx
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import datetime
import os
import bcrypt

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./reflx.db")
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin_user = (
            session.query(AdminUser).filter(AdminUser.username == "admin").first()
        )
        if not admin_user:
            hashed_password = bcrypt.hashpw(
                "admin".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            new_admin = AdminUser(username="admin", password_hash=hashed_password)
            session.add(new_admin)
            session.commit()
        courier = session.get(Courier, 123)
        if not courier:
            new_courier = Courier(
                id=123,
                name="Alex Doe",
                phone="+1-800-555-0101",
                contact_link="https://t.me/alex_courier",
                created_at=datetime.datetime.utcnow(),
            )
            session.add(new_courier)
            session.commit()


class Courier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    contact_link: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    courier_id: int = Field(foreign_key="courier.id")
    rating: int
    comment: Optional[str] = None
    reasons: str
    publish_consent: bool
    needs_follow_up: bool
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)