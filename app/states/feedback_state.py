"""Feedback form state with offline support."""
import reflex as rx
from typing import Optional, cast
from sqlalchemy import text
import json
import asyncio
import logging
from datetime import datetime

from app.database import Courier, engine
from app.utils import QueueManager, validate_feedback_data, generate_request_id
from config import config

class FeedbackState(rx.State):
    """State management for feedback submission with offline queue."""

    # Form fields
    order_id: str = ""
    courier_id: int = 0
    rating: int = 0
    comment: str = ""
    reasons: list[str] = []
    publish_consent: bool = False

    # UI state
    submission_status: str = "idle"
    error_message: str = ""
    courier: Optional[dict] = None
    is_online: bool = True

    # Toast notifications
    toast_message: str = ""
    toast_type: str = "info"  # info, success, warning, error
    show_toast: bool = False

    # Local storage queue (persists across sessions)
    pending_queue: list[dict] = rx.LocalStorage([])
    syncing: bool = False

    @rx.var
    def comment_length(self) -> int:
        """Get current comment length."""
        return len(self.comment)

    @rx.var
    def is_form_valid(self) -> bool:
        """Validate form completeness."""
        return self.rating > 0 and self.comment_length <= 500

    @rx.var
    def pending_count(self) -> int:
        """Get count of pending offline submissions."""
        return len(self.pending_queue)

    @rx.var
    def can_submit(self) -> bool:
        """Check if submission is allowed."""
        return (
            self.is_form_valid
            and self.submission_status not in ["submitting", "syncing"]
            and len(self.pending_queue) < config.MAX_QUEUE_SIZE
        )

    @rx.event
    async def on_load(self):
        """Handle page load, get URL params, and fetch courier info."""
        # Check online status
        self.is_online = True  # Will be updated by JS

        # Parse URL parameters
        self.order_id = self.router.page.params.get("order_id", "")
        try:
            self.courier_id = int(self.router.page.params.get("courier_id", "0"))
        except (ValueError, TypeError) as e:
            logging.exception(f"Invalid courier_id parameter: {e}")
            self.courier_id = 0
            self.submission_status = "error"
            self.error_message = "Invalid Courier ID."
            self._show_toast("Invalid courier ID in URL", "error")
            return

        if not self.order_id or self.courier_id == 0:
            self.submission_status = "error"
            self.error_message = "Missing Order or Courier ID."
            self._show_toast("Missing order or courier information", "error")
            return

        # Load courier and check existing feedback
        yield FeedbackState.check_existing_feedback

        # Process any pending queue items
        if config.ENABLE_OFFLINE_MODE:
            yield FeedbackState.process_queue

    @rx.event(background=True)
    async def check_existing_feedback(self):
        """Check if feedback for this order already exists."""
        async with self:
            from sqlmodel import Session

            with Session(engine) as session:
                # Check for duplicate
                result = session.execute(
                    text("SELECT 1 FROM feedback WHERE order_id = :order_id"),
                    {"order_id": self.order_id},
                )
                existing_feedback = result.scalar_one_or_none()

                if existing_feedback:
                    self.submission_status = "duplicate"
                    self._show_toast("Feedback already submitted for this order", "warning")
                else:
                    self.submission_status = "idle"

                    # Fetch courier information
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
                        self._show_toast("Courier not found", "error")

    @rx.event
    def set_rating(self, value: int):
        """Set rating value."""
        self.rating = value

    @rx.event
    def toggle_reason(self, reason: str):
        """Toggle reason selection."""
        if reason in self.reasons:
            self.reasons.remove(reason)
        else:
            self.reasons.append(reason)

    @rx.event
    def set_publish_consent(self, value: bool):
        """Set publish consent."""
        self.publish_consent = value

    @rx.event
    def set_comment(self, value: str):
        """Set comment value."""
        self.comment = value

    def _show_toast(self, message: str, toast_type: str = "info"):
        """Show toast notification."""
        self.toast_message = message
        self.toast_type = toast_type
        self.show_toast = True

    @rx.event
    def hide_toast(self):
        """Hide toast notification."""
        self.show_toast = False

    @rx.event
    def update_online_status(self, is_online: bool):
        """Update online status from JavaScript."""
        self.is_online = is_online
        if is_online and len(self.pending_queue) > 0:
            self._show_toast(f"Back online! Syncing {len(self.pending_queue)} pending items...", "info")
            return FeedbackState.process_queue

    @rx.event(background=True)
    async def submit_feedback(self):
        """Submit feedback with offline queue support."""
        async with self:
            if not self.can_submit:
                self._show_toast("Please complete all required fields", "warning")
                return

            self.submission_status = "submitting"

            # Prepare feedback data
            feedback_data = {
                "order_id": self.order_id,
                "courier_id": self.courier_id,
                "rating": self.rating,
                "comment": self.comment,
                "reasons": self.reasons,
                "publish_consent": self.publish_consent,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": generate_request_id({
                    "order_id": self.order_id,
                    "courier_id": self.courier_id
                })
            }

            # Validate data
            is_valid, error_msg = validate_feedback_data(feedback_data)
            if not is_valid:
                self.submission_status = "error"
                self.error_message = error_msg
                self._show_toast(error_msg, "error")
                return

        # Simulate network delay
        await asyncio.sleep(0.5)

        async with self:
            try:
                from sqlmodel import Session

                with Session(engine) as session:
                    # Check for duplicate again
                    result = session.execute(
                        text("SELECT 1 FROM feedback WHERE order_id = :order_id"),
                        {"order_id": self.order_id},
                    )
                    if result.scalar_one_or_none():
                        self.submission_status = "duplicate"
                        self._show_toast("Feedback already exists", "warning")
                        return

                    # Insert feedback
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
                self._show_toast("Feedback submitted successfully!", "success")

                # Remove from queue if it was queued
                self.pending_queue = QueueManager.remove_from_queue(
                    self.pending_queue,
                    feedback_data
                )

            except Exception as e:
                logging.exception(f"Submission error: {e}")

                # Check if offline
                if not self.is_online or "connection" in str(e).lower():
                    # Add to offline queue
                    if config.ENABLE_OFFLINE_MODE:
                        self.pending_queue = QueueManager.add_to_queue(
                            self.pending_queue,
                            feedback_data,
                            config.MAX_QUEUE_SIZE
                        )
                        self.submission_status = "queued"
                        self._show_toast(
                            f"Saved offline. Will sync when connected ({len(self.pending_queue)} pending)",
                            "info"
                        )
                    else:
                        self.submission_status = "error"
                        self.error_message = "No internet connection"
                        self._show_toast("No internet connection", "error")
                else:
                    # Other error
                    self.submission_status = "error"
                    self.error_message = f"Failed to submit: {str(e)}"
                    self._show_toast(f"Error: {str(e)}", "error")

    @rx.event(background=True)
    async def process_queue(self):
        """Process pending offline submissions."""
        async with self:
            if self.syncing or not self.is_online or len(self.pending_queue) == 0:
                return

            self.syncing = True
            logging.info(f"Processing {len(self.pending_queue)} queued items...")

        synced_count = 0
        failed_items = []

        for item in self.pending_queue[:]:  # Copy to avoid mutation issues
            try:
                from sqlmodel import Session

                with Session(engine) as session:
                    # Check for duplicate
                    result = session.execute(
                        text("SELECT 1 FROM feedback WHERE order_id = :order_id"),
                        {"order_id": item["order_id"]},
                    )

                    if result.scalar_one_or_none():
                        # Already exists, remove from queue
                        async with self:
                            self.pending_queue = QueueManager.remove_from_queue(
                                self.pending_queue,
                                item
                            )
                        continue

                    # Insert feedback
                    needs_follow_up = item["rating"] <= 4
                    session.execute(
                        text(
                            "INSERT INTO feedback (order_id, courier_id, rating, comment, reasons, publish_consent, needs_follow_up, created_at) VALUES (:order_id, :courier_id, :rating, :comment, :reasons, :publish_consent, :needs_follow_up, CURRENT_TIMESTAMP)"
                        ),
                        {
                            "order_id": item["order_id"],
                            "courier_id": item["courier_id"],
                            "rating": item["rating"],
                            "comment": item.get("comment", ""),
                            "reasons": json.dumps(item.get("reasons", [])),
                            "publish_consent": item.get("publish_consent", False),
                            "needs_follow_up": needs_follow_up,
                        },
                    )
                    session.commit()

                # Success - remove from queue
                async with self:
                    self.pending_queue = QueueManager.remove_from_queue(
                        self.pending_queue,
                        item
                    )
                    synced_count += 1

                logging.info(f"Successfully synced order {item['order_id']}")

            except Exception as e:
                logging.exception(f"Queue sync error for {item.get('order_id')}: {e}")
                failed_items.append(item)
                # Keep in queue for retry

        async with self:
            self.syncing = False

            if synced_count > 0:
                self._show_toast(
                    f"✓ Synced {synced_count} feedback item(s)",
                    "success"
                )

            if len(failed_items) > 0:
                logging.warning(f"{len(failed_items)} items failed to sync")

    @rx.event(background=True)
    async def seed_data(self):
        """Seed the database with a sample courier."""
        async with self:
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
                    self._show_toast("Sample courier data seeded", "success")
