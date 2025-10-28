"""Business logic services for the application."""
import json
import logging
from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.database import Courier, Feedback, AdminUser, engine, verify_password

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for feedback operations."""

    @staticmethod
    def create_feedback(feedback_data: dict) -> Feedback:
        """Create new feedback entry."""
        try:
            with Session(engine) as session:
                # Check for duplicate
                order_id = feedback_data.get("order_id")
                existing = session.exec(
                    select(Feedback).where(Feedback.order_id == order_id)
                ).first()

                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Feedback for this order already exists."
                    )

                # Auto-flag low ratings for follow-up
                rating = feedback_data.get("rating", 0)
                needs_follow_up = rating <= 4

                # Create feedback
                feedback = Feedback(
                    order_id=order_id,
                    courier_id=feedback_data.get("courier_id"),
                    rating=rating,
                    comment=feedback_data.get("comment"),
                    reasons=json.dumps(feedback_data.get("reasons", [])),
                    publish_consent=feedback_data.get("publish_consent", False),
                    needs_follow_up=needs_follow_up,
                )

                session.add(feedback)
                session.commit()
                session.refresh(feedback)

                logger.info(f"Feedback created for order {order_id}")
                return feedback

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating feedback: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create feedback"
            )

    @staticmethod
    def get_feedback(feedback_id: int) -> Feedback:
        """Get feedback by ID."""
        with Session(engine) as session:
            feedback = session.get(Feedback, feedback_id)
            if not feedback:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Feedback not found"
                )
            return feedback

    @staticmethod
    def list_feedback(courier_id: Optional[int] = None) -> List[Feedback]:
        """List all feedback, optionally filtered by courier."""
        with Session(engine) as session:
            query = select(Feedback)
            if courier_id:
                query = query.where(Feedback.courier_id == courier_id)
            return list(session.exec(query).all())


class CourierService:
    """Service for courier operations."""

    @staticmethod
    def get_courier(courier_id: int) -> Courier:
        """Get courier by ID."""
        with Session(engine) as session:
            courier = session.get(Courier, courier_id)
            if not courier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Courier not found"
                )
            return courier


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[AdminUser]:
        """Authenticate admin user."""
        with Session(engine) as session:
            admin = session.exec(
                select(AdminUser).where(AdminUser.username == username)
            ).first()

            if admin and verify_password(password, admin.password_hash):
                return admin
            return None
