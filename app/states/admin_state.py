import reflex as rx
from typing import Optional
import bcrypt
from sqlmodel import Session, select, text
from ..database import AdminUser, Feedback, Courier, engine
import csv
import io
import datetime
import logging
import json


logger = logging.getLogger(__name__)


class AdminState(rx.State):
    is_authenticated: bool = False
    username: str = ""
    password: str = ""
    error_message: str = ""
    feedbacks: list[dict] = []
    filter_from_date: str = ""
    filter_to_date: str = ""
    filter_ratings: list[int] = []

    @rx.var
    def filtered_feedbacks(self) -> list[dict]:
        """Filter feedbacks based on current filter settings."""
        feedbacks = self.feedbacks

        if self.filter_from_date:
            try:
                from_date = datetime.datetime.fromisoformat(
                    self.filter_from_date
                ).date()
                feedbacks = [
                    f
                    for f in feedbacks
                    if datetime.datetime.fromisoformat(f["created_at"]).date()
                    >= from_date
                ]
            except (ValueError, TypeError) as e:
                logger.exception(f"Error parsing from_date: {e}")

        if self.filter_to_date:
            try:
                to_date = datetime.datetime.fromisoformat(self.filter_to_date).date()
                feedbacks = [
                    f
                    for f in feedbacks
                    if datetime.datetime.fromisoformat(f["created_at"]).date()
                    <= to_date
                ]
            except (ValueError, TypeError) as e:
                logger.exception(f"Error parsing to_date: {e}")

        if self.filter_ratings:
            feedbacks = [f for f in feedbacks if f["rating"] in self.filter_ratings]

        return feedbacks

    @rx.var
    def parsed_feedbacks(self) -> list[dict]:
        """Parse JSON reasons field for display."""
        parsed_data = []
        for feedback in self.filtered_feedbacks:
            new_feedback = feedback.copy()
            try:
                reasons_str = new_feedback.get("reasons", "[]")
                new_feedback["reasons"] = json.loads(reasons_str) if reasons_str else []
            except (json.JSONDecodeError, TypeError) as e:
                logger.exception(f"Error parsing reasons: {e}")
                new_feedback["reasons"] = []
            parsed_data.append(new_feedback)
        return parsed_data

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @rx.event
    async def login(self, form_data: dict):
        """Handle admin login."""
        self.username = form_data.get("username", "")
        self.password = form_data.get("password", "")

        with Session(engine) as session:
            admin_user = session.exec(
                select(AdminUser).where(AdminUser.username == self.username)
            ).first()

        if admin_user and self._verify_password(self.password, admin_user.password_hash):
            self.is_authenticated = True
            self.error_message = ""
            self.password = ""  # Clear password from state
            return rx.redirect("/admin/dashboard")
        else:
            self.error_message = "Invalid username or password."
            self.password = ""

    @rx.event
    def logout(self):
        """Handle admin logout."""
        self.is_authenticated = False
        self.username = ""
        self.password = ""
        self.feedbacks = []
        self.filter_from_date = ""
        self.filter_to_date = ""
        self.filter_ratings = []
        return rx.redirect("/admin")

    # FIXED: Combined auth check and data loading
    @rx.event
    async def check_auth_and_load(self):
        """Check authentication and load feedback data."""
        if not self.is_authenticated:
            return rx.redirect("/admin")

        # Load feedback data
        await self.load_feedback()

    @rx.event
    async def load_feedback(self):
        """Load feedback data from database."""
        try:
            with Session(engine) as session:
                stmt = text("""
                    SELECT
                        f.id,
                        f.order_id,
                        c.name as courier_name,
                        f.rating,
                        f.comment,
                        f.reasons,
                        f.publish_consent,
                        f.needs_follow_up,
                        f.created_at
                    FROM feedback f
                    JOIN courier c ON f.courier_id = c.id
                    ORDER BY f.created_at DESC
                """)
                results = session.exec(stmt).mappings().all()
                self.feedbacks = [dict(row) for row in results]
                logger.info(f"Loaded {len(self.feedbacks)} feedback entries")
        except Exception as e:
            logger.exception(f"Error loading feedback: {e}")
            self.feedbacks = []

    @rx.event
    def toggle_rating_filter(self, rating: int):
        """Toggle rating filter on/off."""
        if rating in self.filter_ratings:
            self.filter_ratings.remove(rating)
        else:
            self.filter_ratings.append(rating)

    @rx.event
    def reset_filters(self):
        """Reset all filters to default."""
        self.filter_from_date = ""
        self.filter_to_date = ""
        self.filter_ratings = []

    @rx.event
    def get_csv(self):
        """Export filtered feedback as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        headers = [
            "ID",
            "Order ID",
            "Courier Name",
            "Rating",
            "Comment",
            "Reasons",
            "Consent",
            "Needs Follow-up",
            "Date",
        ]
        writer.writerow(headers)

        # Write data
        for feedback in self.filtered_feedbacks:
            writer.writerow(
                [
                    feedback.get("id", ""),
                    feedback.get("order_id", ""),
                    feedback.get("courier_name", ""),
                    feedback.get("rating", ""),
                    feedback.get("comment", ""),
                    feedback.get("reasons", ""),
                    feedback.get("publish_consent", ""),
                    feedback.get("needs_follow_up", ""),
                    feedback.get("created_at", ""),
                ]
            )

        # FIXED: Return download with proper encoding
        csv_data = output.getvalue()
        return rx.download(
            data=csv_data,
            filename=f"feedback_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
