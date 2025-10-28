"""Tests for service layer."""
import pytest
import json
from fastapi import HTTPException

from app.services import FeedbackService, CourierService, AuthService
from app.database import Feedback, Courier, AdminUser, hash_password


class TestFeedbackService:
    """Tests for FeedbackService."""

    def test_create_feedback_success(self, db_session, sample_courier, monkeypatch):
        """Test successful feedback creation."""
        # Mock the engine
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        data = {
            "order_id": "NEW001",
            "courier_id": sample_courier.id,
            "rating": 5,
            "comment": "Excellent!",
            "reasons": ["Punctuality", "Politeness"],
            "publish_consent": True
        }

        result = FeedbackService.create_feedback(data)

        assert result.order_id == "NEW001"
        assert result.rating == 5
        assert result.needs_follow_up is False

    def test_create_feedback_duplicate(self, db_session, sample_feedback, monkeypatch):
        """Test creating duplicate feedback raises error."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        data = {
            "order_id": sample_feedback.order_id,  # Duplicate
            "courier_id": sample_feedback.courier_id,
            "rating": 4,
            "reasons": [],
            "publish_consent": False
        }

        with pytest.raises(HTTPException) as exc_info:
            FeedbackService.create_feedback(data)

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail

    def test_create_feedback_low_rating_flags_followup(self, db_session, sample_courier, monkeypatch):
        """Test low rating automatically flags for follow-up."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        data = {
            "order_id": "LOW001",
            "courier_id": sample_courier.id,
            "rating": 3,  # Low rating
            "reasons": [],
            "publish_consent": False
        }

        result = FeedbackService.create_feedback(data)

        assert result.needs_follow_up is True

    def test_get_feedback_success(self, db_session, sample_feedback, monkeypatch):
        """Test getting feedback by ID."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = FeedbackService.get_feedback(sample_feedback.id)

        assert result.id == sample_feedback.id
        assert result.order_id == sample_feedback.order_id

    def test_get_feedback_not_found(self, db_session, monkeypatch):
        """Test getting non-existent feedback."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        with pytest.raises(HTTPException) as exc_info:
            FeedbackService.get_feedback(999)

        assert exc_info.value.status_code == 404

    def test_list_feedback_all(self, db_session, sample_feedback, monkeypatch):
        """Test listing all feedback."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = FeedbackService.list_feedback()

        assert len(result) >= 1
        assert any(f.id == sample_feedback.id for f in result)

    def test_list_feedback_filtered_by_courier(self, db_session, sample_courier, monkeypatch):
        """Test listing feedback filtered by courier."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        # Create feedback for specific courier
        feedback = Feedback(
            order_id="FILTER001",
            courier_id=sample_courier.id,
            rating=5
        )
        db_session.add(feedback)
        db_session.commit()

        result = FeedbackService.list_feedback(courier_id=sample_courier.id)

        assert all(f.courier_id == sample_courier.id for f in result)

    def test_create_feedback_invalid_rating(self, db_session, sample_courier, monkeypatch):
        """Test creating feedback with invalid rating raises error."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        data = {
            "order_id": "INVALID_RATING",
            "courier_id": sample_courier.id,
            "rating": 6,  # Invalid rating
            "reasons": [],
            "publish_consent": False
        }

        with pytest.raises(HTTPException) as exc_info:
            FeedbackService.create_feedback(data)

        assert exc_info.value.status_code == 422


class TestCourierService:
    """Tests for CourierService."""

    def test_get_courier_success(self, db_session, sample_courier, monkeypatch):
        """Test getting courier by ID."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = CourierService.get_courier(sample_courier.id)

        assert result.id == sample_courier.id
        assert result.name == sample_courier.name

    def test_get_courier_not_found(self, db_session, monkeypatch):
        """Test getting non-existent courier."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        with pytest.raises(HTTPException) as exc_info:
            CourierService.get_courier(999)

        assert exc_info.value.status_code == 404


class TestAuthService:
    """Tests for AuthService."""

    def test_authenticate_success(self, db_session, sample_admin, monkeypatch):
        """Test successful authentication."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = AuthService.authenticate("testadmin", "testpass123")

        assert result is not None
        assert result.username == "testadmin"

    def test_authenticate_wrong_password(self, db_session, sample_admin, monkeypatch):
        """Test authentication with wrong password."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = AuthService.authenticate("testadmin", "wrongpassword")

        assert result is None

    def test_authenticate_nonexistent_user(self, db_session, monkeypatch):
        """Test authentication with non-existent user."""
        monkeypatch.setattr("app.services.engine", db_session.get_bind())

        result = AuthService.authenticate("nonexistent", "password")

        assert result is None
