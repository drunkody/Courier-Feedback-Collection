import reflex as rx
from typing import Optional, cast
from sqlalchemy import text
import json
from ..database import Courier
import asyncio
import logging


class FeedbackState(rx.State):
    order_id: str = ""
    courier_id: int = 0
    rating: int = 0
    comment: str = ""
    reasons: list[str] = []
    publish_consent: bool = False
    submission_status: str = "idle"
    error_message: str = ""
    courier: Optional[dict] = None

    @rx.var
    def comment_length(self) -> int:
        return len(self.comment)

    @rx.var
    def is_form_valid(self) -> bool:
        return self.rating > 0 and self.comment_length <= 500

    @rx.event
    async def on_load(self):
        """Handle page load, get URL params, and fetch courier info."""
        self.order_id = self.router.page.params.get("order_id", "")
        try:
            self.courier_id = int(self.router.page.params.get("courier_id", "0"))
        except (ValueError, TypeError) as e:
            logging.exception(f"Error: {e}")
            self.courier_id = 0
            self.submission_status = "error"
            self.error_message = "Invalid Courier ID."
            return
        if not self.order_id or self.courier_id == 0:
            self.submission_status = "error"
            self.error_message = "Missing Order or Courier ID."
            return
        yield FeedbackState.check_existing_feedback

    @rx.event(background=True)
    async def check_existing_feedback(self):
        """Check if feedback for this order already exists."""
        async with self:
            from ..database import engine
            from sqlmodel import Session

            with Session(engine) as session:
                result = session.execute(
                    text("SELECT 1 FROM feedback WHERE order_id = :order_id"),
                    {"order_id": self.order_id},
                )
                existing_feedback = result.scalar_one_or_none()
                if existing_feedback:
                    self.submission_status = "duplicate"
                else:
                    self.submission_status = "idle"
                    courier_result = session.execute(
                        text(
                            "SELECT id, name, phone, contact_link FROM courier WHERE id = :courier_id"
                        ),
                        {"courier_id": self.courier_id},
                    )
                    courier_data = courier_result.first()
                    if courier_data:
                        self.courier = cast(
                            Courier,
                            {
                                "id": courier_data[0],
                                "name": courier_data[1],
                                "phone": courier_data[2],
                                "contact_link": courier_data[3],
                            },
                        )
                    else:
                        self.submission_status = "error"
                        self.error_message = "Courier not found."

    @rx.event
    def set_rating(self, value: int):
        self.rating = value

    @rx.event
    def toggle_reason(self, reason: str):
        if reason in self.reasons:
            self.reasons.remove(reason)
        else:
            self.reasons.append(reason)

    @rx.event(background=True)
    async def submit_feedback(self):
        async with self:
            if not self.is_form_valid:
                return
            self.submission_status = "submitting"
        await asyncio.sleep(1)
        async with self:
            try:
                from ..database import engine
                from sqlmodel import Session

                with Session(engine) as session:
                    result = session.execute(
                        text("SELECT 1 FROM feedback WHERE order_id = :order_id"),
                        {"order_id": self.order_id},
                    )
                    if result.scalar_one_or_none():
                        self.submission_status = "duplicate"
                        return
                    needs_follow_up = self.rating <= 4
                    session.execute(
                        text(
                            "INSERT INTO feedback (order_id, courier_id, rating, comment, reasons, publish_consent, needs_follow_up, created_at) VALUES (:order_id, :courier_id, :rating, :comment, :reasons, :publish_consent, :needs_follow_up, CURRENT_TIMESTAMP)"
                        ),
                        {
                            "order_id": self.order_id,
                            "courier_id": self.courier_id,
                            "rating": self.rating,
                            "comment": self.comment,
                            "reasons": json.dumps(self.reasons),
                            "publish_consent": self.publish_consent,
                            "needs_follow_up": needs_follow_up,
                        },
                    )
                    session.commit()
                self.submission_status = "success"
            except Exception as e:
                logging.exception(f"Error: {e}")
                self.submission_status = "error"
                self.error_message = f"An unexpected error occurred: {str(e)}"

    @rx.event(background=True)
    async def seed_data(self):
        """Seed the database with a sample courier."""
        async with self:
            from ..database import engine
            from sqlmodel import Session

            with Session(engine) as session:
                result = session.execute(
                    text("SELECT 1 FROM courier WHERE id = :id"), {"id": 123}
                )
                if not result.scalar_one_or_none():
                    session.execute(
                        text(
                            "INSERT INTO courier (id, name, phone, contact_link, created_at) VALUES (:id, :name, :phone, :contact_link, :created_at)"
                        ),
                        {
                            "id": 123,
                            "name": "Alex Doe",
                            "phone": "+1-800-555-0101",
                            "contact_link": "https://t.me/alex_courier",
                            "created_at": "2023-01-01 00:00:00",
                        },
                    )
                    session.commit()