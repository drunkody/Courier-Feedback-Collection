"""Tests for database models."""
import pytest
from datetime import datetime
import json
from sqlmodel import Session

from app.database import Courier, Feedback, AdminUser, hash_password, verify_password


class TestCourierModel:
    """Tests for Courier model."""

    def test_create_courier(self, db_session):
        """Test creating a courier."""
        courier = Courier(
            name="John Doe",
            phone="+1-555-0100",
            contact_link="https://example.com"
        )
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)

        assert courier.id is not None
        assert courier.name == "John Doe"
        assert courier.phone == "+1-555-0100"
        assert courier.created_at is not None

    def test_courier_without_contact_link(self, db_session):
        """Test courier without optional contact link."""
        courier = Courier(
            name="Jane Doe",
            phone="+1-555-0101"
        )
        db_session.add(courier)
        db_session.commit()

        assert courier.contact_link is None

    def test_courier_created_at_auto(self, db_session):
        """Test created_at is automatically set."""
        before = datetime.utcnow()
        courier = Courier(name="Test", phone="+1-555-0100")
        db_session.add(courier)
        db_session.commit()
        after = datetime.utcnow()

        assert before <= courier.created_at <= after


class TestFeedbackModel:
    """Tests for Feedback model."""

    def test_create_feedback(self, db_session, sample_courier):
        """Test creating feedback."""
        feedback = Feedback(
            order_id="TEST001",
            courier_id=sample_courier.id,
            rating=5,
            comment="Great!",
            reasons=json.dumps(["Punctuality"]),
            publish_consent=True,
            needs_follow_up=False
        )
        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(feedback)

        assert feedback.id is not None
        assert feedback.order_id == "TEST001"
        assert feedback.rating == 5

    def test_feedback_unique_order_id(self, db_session, sample_courier):
        """Test order_id uniqueness constraint."""
        feedback1 = Feedback(
            order_id="DUPLICATE",
            courier_id=sample_courier.id,
            rating=5
        )
        db_session.add(feedback1)
        db_session.commit()

        feedback2 = Feedback(
            order_id="DUPLICATE",
            courier_id=sample_courier.id,
            rating=4
        )
        db_session.add(feedback2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_feedback_needs_follow_up_flag(self, db_session, sample_courier):
        """Test needs_follow_up for low ratings."""
        # Rating <= 4 should flag for follow-up
        feedback = Feedback(
            order_id="TEST003",
            courier_id=sample_courier.id,
            rating=3,
            needs_follow_up=True
        )
        db_session.add(feedback)
        db_session.commit()

        assert feedback.needs_follow_up is True

    def test_feedback_default_values(self, db_session, sample_courier):
        """Test default values for optional fields."""
        feedback = Feedback(
            order_id="TEST004",
            courier_id=sample_courier.id,
            rating=5
        )
        db_session.add(feedback)
        db_session.commit()

        assert feedback.comment is None
        assert feedback.reasons == "[]"
        assert feedback.publish_consent is False
        assert feedback.needs_follow_up is False


class TestAdminUserModel:
    """Tests for AdminUser model."""

    def test_create_admin_user(self, db_session):
        """Test creating admin user."""
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("password123")
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

        assert admin.id is not None
        assert admin.username == "admin"
        assert admin.password_hash is not None

    def test_username_unique(self, db_session):
        """Test username uniqueness constraint."""
        admin1 = AdminUser(
            username="duplicate",
            password_hash=hash_password("pass1")
        )
        db_session.add(admin1)
        db_session.commit()

        admin2 = AdminUser(
            username="duplicate",
            password_hash=hash_password("pass2")
        )
        db_session.add(admin2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_password_hashing(self):
        """Test password is hashed correctly."""
        password = "mypassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)

    def test_password_verification_fails(self):
        """Test incorrect password verification."""
        password = "correct"
        wrong_password = "incorrect"
        hashed = hash_password(password)

        assert not verify_password(wrong_password, hashed)
