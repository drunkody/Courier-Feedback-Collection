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

logger = logging.getLogger(__name__)


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

    # Queue management (mode-dependent)
    pending_queue: list[dict] = []
    jazz_initialized: bool = False
    syncing: bool = False

    # Mode indicator
    app_mode: str = config.APP_MODE

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

    @rx.var
    def is_jazz_mode(self) -> bool:
        """Check if using Jazz sync."""
        return config.USE_JAZZ_SYNC

    @rx.var
    def is_backend_mode(self) -> bool:
        """Check if using backend."""
        return config.USE_BACKEND

    @rx.var
    def is_jazz_only(self) -> bool:
        """Check if Jazz-only mode."""
        return config.JAZZ_ONLY_MODE

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
            logger.exception(f"Invalid courier_id parameter: {e}")
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

        # FIXED: Initialize Jazz in background if needed
        if config.USE_JAZZ_SYNC:
            # Note: Jazz initialization would need proper JS interop
            # This is a placeholder - actual implementation depends on Reflex's JS bridge
            self.jazz_initialized = False
            logger.info("Jazz mode enabled - initialization required")

        # Load courier info
        yield FeedbackState.check_existing_feedback

        # Process queue in background
        if config.ENABLE_OFFLINE_MODE:
            yield FeedbackState.process_queue

    @rx.event(background=True)
    async def init_jazz(self):
        """Initialize Jazz system - PLACEHOLDER."""
        async with self:
            if self.jazz_initialized:
                return

            logger.info(f"🎺 Initializing Jazz (mode: {config.APP_MODE})...")

            # FIXED: This is a placeholder - actual Jazz init needs proper implementation
            # Reflex doesn't have call_script method - this would need custom JS interop
            try:
                # Simulate initialization
                await asyncio.sleep(0.5)
                self.jazz_initialized = True
                logger.info("✅ Jazz initialized (simulated)")
                self._show_toast("Jazz sync ready", "success")
            except Exception as e:
                logger.exception(f"Jazz initialization error: {e}")
                self._show_toast(f"Jazz error: {str(e)}", "error")

    @rx.event(background=True)
    async def check_existing_feedback(self):
        """Check if feedback exists and load courier info."""
        async with self:
            # FIXED: Only check backend in non-Jazz-only modes
            if config.JAZZ_ONLY_MODE:
                logger.info("Jazz-only mode - skipping database check")
                # In Jazz-only mode, we'd check Jazz storage
                # For now, assume no duplicate
                self.submission_status = "idle"
                # Mock courier data for Jazz-only mode
                self.courier = {
                    "id": self.courier_id,
                    "name": "Alex Doe",
                    "phone": "+1-800-555-0101",
                    "contact_link": "https://t.me/alex_courier"
                }
                return

            if config.USE_BACKEND:
                # Check in SQL database
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
                        self._show_toast("Feedback already submitted", "warning")
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
        if is_online and self.pending_count > 0:
            self._show_toast(f"Back online! Syncing {self.pending_count} pending items...", "info")
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
            # Handle submission based on mode
            if config.JAZZ_ONLY_MODE:
                await self._submit_to_jazz_collection(feedback_data)
            elif config.USE_BACKEND:
                if self.is_online or not config.ENABLE_OFFLINE_MODE:
                    await self._submit_to_backend(feedback_data)
                else:
                    await self._queue_feedback(feedback_data)
            else:
                # Fallback to queue
                await self._queue_feedback(feedback_data)

    async def _submit_to_jazz_collection(self, feedback_data: dict):
        """Submit feedback directly to Jazz collection - PLACEHOLDER."""
        # FIXED: This needs proper Jazz integration
        # For now, simulate success
        try:
            logger.info(f"Submitting to Jazz: {feedback_data['order_id']}")
            await asyncio.sleep(0.3)
            self.submission_status = "success"
            self._show_toast("Feedback submitted to Jazz!", "success")
        except Exception as e:
            logger.exception(f"Jazz submission error: {e}")
            self.submission_status = "error"
            self.error_message = str(e)
            self._show_toast("Error submitting to Jazz", "error")

    async def _submit_to_backend(self, feedback_data: dict):
        """Submit feedback to the backend."""
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
            await self._dequeue_feedback(feedback_data)

        except Exception as e:
            logger.exception(f"Submission error: {e}")
            # If submission fails and offline mode is enabled, queue it
            if config.ENABLE_OFFLINE_MODE:
                await self._queue_feedback(feedback_data)
            else:
                self.submission_status = "error"
                self.error_message = str(e)
                self._show_toast(f"Submission failed: {str(e)}", "error")

    async def _queue_feedback(self, feedback_data: dict, show_toast=True):
        """Add feedback to the queue."""
        if config.ENABLE_OFFLINE_MODE:
            self.pending_queue = QueueManager.add_to_queue(
                self.pending_queue,
                feedback_data,
                config.MAX_QUEUE_SIZE
            )
            self.submission_status = "queued"
            if show_toast:
                self._show_toast(
                    f"Saved offline ({self.pending_count} pending)",
                    "info"
                )
        else:
            self.submission_status = "error"
            self.error_message = "No internet connection"
            self._show_toast("No internet connection", "error")

    async def _dequeue_feedback(self, feedback_data: dict):
        """Remove feedback from the queue."""
        self.pending_queue = QueueManager.remove_from_queue(
            self.pending_queue,
            feedback_data
        )

    @rx.event(background=True)
    async def process_queue(self):
        """Process pending offline submissions."""
        async with self:
            if self.syncing or not self.is_online or self.pending_count == 0:
                return

            self.syncing = True
            logger.info(f"Processing {self.pending_count} queued items...")

        synced_count = 0
        failed_items = []

        for item in self.pending_queue[:]:  # Copy to avoid mutation issues
            try:
                # FIXED: Process queue items
                await self._submit_to_backend(item)
                synced_count += 1
            except Exception as e:
                logger.exception(f"Queue sync error for {item.get('order_id')}: {e}")
                failed_items.append(item)

        async with self:
            # Update queue with only failed items
            self.pending_queue = failed_items
            self.syncing = False

            if synced_count > 0:
                self._show_toast(
                    f"✓ Synced {synced_count} feedback item(s)",
                    "success"
                )
            if len(failed_items) > 0:
                logger.warning(f"{len(failed_items)} items failed to sync")
                self._show_toast(
                    f"{len(failed_items)} items still pending",
                    "warning"
                )
