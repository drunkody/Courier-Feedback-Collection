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
            except ValueError as e:
                logging.exception(f"Error: {e}")
        if self.filter_to_date:
            try:
                to_date = datetime.datetime.fromisoformat(self.filter_to_date).date()
                feedbacks = [
                    f
                    for f in feedbacks
                    if datetime.datetime.fromisoformat(f["created_at"]).date()
                    <= to_date
                ]
            except ValueError as e:
                logging.exception(f"Error: {e}")
        if self.filter_ratings:
            feedbacks = [f for f in feedbacks if f["rating"] in self.filter_ratings]
        return feedbacks

    @rx.var
    def parsed_feedbacks(self) -> list[dict]:
        parsed_data = []
        for feedback in self.filtered_feedbacks:
            new_feedback = feedback.copy()
            try:
                new_feedback["reasons"] = json.loads(new_feedback.get("reasons", "[]"))
            except (json.JSONDecodeError, TypeError) as e:
                logging.exception(f"Error parsing reasons: {e}")
                new_feedback["reasons"] = []
            parsed_data.append(new_feedback)
        return parsed_data

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @rx.event
    async def login(self, form_data: dict):
        self.username = form_data.get("username", "")
        self.password = form_data.get("password", "")
        with Session(engine) as session:
            admin_user = session.exec(
                select(AdminUser).where(AdminUser.username == self.username)
            ).first()
        if admin_user and self._verify_password(
            self.password, admin_user.password_hash
        ):
            self.is_authenticated = True
            self.error_message = ""
            self.password = ""
            return rx.redirect("/admin/dashboard")
        else:
            self.error_message = "Invalid username or password."
            self.password = ""

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.username = ""
        self.password = ""
        self.feedbacks = []
        return rx.redirect("/admin")

    @rx.event
    async def check_auth(self):
        if not self.is_authenticated:
            yield rx.redirect("/admin")
            return
        yield AdminState.load_feedback

    @rx.event
    async def load_feedback(self):
        with Session(engine) as session:
            stmt = text("""
                    SELECT f.id, f.order_id, c.name as courier_name, f.rating, f.comment, f.reasons, f.publish_consent, f.needs_follow_up, f.created_at
                    FROM feedback f
                    JOIN courier c ON f.courier_id = c.id
                    ORDER BY f.created_at DESC
                    """)
            results = session.exec(stmt).mappings().all()
            self.feedbacks = [dict(row) for row in results]

    @rx.event
    def toggle_rating_filter(self, rating: int):
        if rating in self.filter_ratings:
            self.filter_ratings.remove(rating)
        else:
            self.filter_ratings.append(rating)

    @rx.event
    def reset_filters(self):
        self.filter_from_date = ""
        self.filter_to_date = ""
        self.filter_ratings = []

    @rx.event
    def get_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
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
        for feedback in self.filtered_feedbacks:
            writer.writerow(
                [
                    feedback["id"],
                    feedback["order_id"],
                    feedback["courier_name"],
                    feedback["rating"],
                    feedback["comment"],
                    feedback["reasons"],
                    feedback["publish_consent"],
                    feedback["needs_follow_up"],
                    feedback["created_at"],
                ]
            )
        return rx.download(data=output.getvalue(), filename="feedback_export.csv")