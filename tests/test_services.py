"""Tests for service layer."""
import pytest
import json
from fastapi import HTTPException
from sqlmodel import Session

from app.services import FeedbackService, CourierService, AuthService
from app.database import Feedback, Courier, AdminUser, hash_password


class TestFeedbackService:
    """Tests for FeedbackService."""

    def test_create_feedback_success(self, db_engine, sample_courier):
        """Test successful feedback creation."""
        # FIXED: Patch at import time
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
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
        finally:
            app.services.engine = original_engine

    def test_create_feedback_duplicate(self, db_engine, sample_feedback):
        """Test creating duplicate feedback raises error."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
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
        finally:
            app.services.engine = original_engine

    def test_create_feedback_low_rating_flags_followup(self, db_engine, sample_courier):
        """Test low rating automatically flags for follow-up."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            data = {
                "order_id": "LOW001",
                "courier_id": sample_courier.id,
                "rating": 3,  # Low rating
                "reasons": [],
                "publish_consent": False
            }

            result = FeedbackService.create_feedback(data)

            assert result.needs_follow_up is True
        finally:
            app.services.engine = original_engine

    def test_get_feedback_success(self, db_engine, sample_feedback):
        """Test getting feedback by ID."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = FeedbackService.get_feedback(sample_feedback.id)

            assert result.id == sample_feedback.id
            assert result.order_id == sample_feedback.order_id
        finally:
            app.services.engine = original_engine

    def test_get_feedback_not_found(self, db_engine):
        """Test getting non-existent feedback."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            with pytest.raises(HTTPException) as exc_info:
                FeedbackService.get_feedback(999)

            assert exc_info.value.status_code == 404
        finally:
            app.services.engine = original_engine

    def test_list_feedback_all(self, db_engine, sample_feedback):
        """Test listing all feedback."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = FeedbackService.list_feedback()

            assert len(result) >= 1
            assert any(f.id == sample_feedback.id for f in result)
        finally:
            app.services.engine = original_engine

    def test_list_feedback_filtered_by_courier(self, db_engine, sample_courier):
        """Test listing feedback filtered by courier."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            # Create feedback for specific courier
            with Session(db_engine) as session:
                feedback = Feedback(
                    order_id="FILTER001",
                    courier_id=sample_courier.id,
                    rating=5
                )
                session.add(feedback)
                session.commit()

            result = FeedbackService.list_feedback(courier_id=sample_courier.id)

            assert all(f.courier_id == sample_courier.id for f in result)
        finally:
            app.services.engine = original_engine

    def test_create_feedback_invalid_rating(self, db_engine, sample_courier):
        """Test creating feedback with invalid rating raises error."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
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
        finally:
            app.services.engine = original_engine


class TestCourierService:
    """Tests for CourierService."""

    def test_get_courier_success(self, db_engine, sample_courier):
        """Test getting courier by ID."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = CourierService.get_courier(sample_courier.id)

            assert result.id == sample_courier.id
            assert result.name == sample_courier.name
        finally:
            app.services.engine = original_engine

    def test_get_courier_not_found(self, db_engine):
        """Test getting non-existent courier."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            with pytest.raises(HTTPException) as exc_info:
                CourierService.get_courier(999)

            assert exc_info.value.status_code == 404
        finally:
            app.services.engine = original_engine


class TestAuthService:
    """Tests for AuthService."""

    def test_authenticate_success(self, db_engine, sample_admin):
        """Test successful authentication."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = AuthService.authenticate("testadmin", "testpass123")

            assert result is not None
            assert result.username == "testadmin"
        finally:
            app.services.engine = original_engine

    def test_authenticate_wrong_password(self, db_engine, sample_admin):
        """Test authentication with wrong password."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = AuthService.authenticate("testadmin", "wrongpassword")

            assert result is None
        finally:
            app.services.engine = original_engine

    def test_authenticate_nonexistent_user(self, db_engine):
        """Test authentication with non-existent user."""
        import app.services
        original_engine = app.services.engine
        app.services.engine = db_engine

        try:
            result = AuthService.authenticate("nonexistent", "password")

            assert result is None
        finally:
            app.services.engine = original_engine
