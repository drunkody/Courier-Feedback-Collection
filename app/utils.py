"""Utility functions and helpers."""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict


def generate_request_id(data: Dict[str, Any]) -> str:
    """Generate unique ID for feedback submission."""
    unique_string = f"{data.get('order_id')}_{data.get('courier_id')}_{datetime.utcnow().isoformat()}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def serialize_feedback(data: Dict[str, Any]) -> str:
    """Serialize feedback data for storage."""
    return json.dumps(data, default=str)


def deserialize_feedback(data: str) -> Dict[str, Any]:
    """Deserialize feedback data from storage."""
    return json.loads(data)


def validate_feedback_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate feedback data structure."""
    required_fields = ["order_id", "courier_id", "rating"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    rating = data.get("rating")
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return False, "Rating must be between 1 and 5"

    comment = data.get("comment", "")
    if len(comment) > 500:
        return False, "Comment exceeds 500 characters"

    return True, ""


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class QueueManager:
    """Manage local storage queue operations."""

    @staticmethod
    def add_to_queue(queue: list, item: dict, max_size: int = 50) -> list:
        """Add item to queue with size limit."""
        if len(queue) >= max_size:
            # Remove oldest item (FIFO)
            queue.pop(0)
        queue.append(item)
        return queue

    @staticmethod
    def remove_from_queue(queue: list, item: dict) -> list:
        """Remove item from queue by matching order_id."""
        return [q for q in queue if q.get("order_id") != item.get("order_id")]

    @staticmethod
    def get_pending_count(queue: list) -> int:
        """Get count of pending items."""
        return len(queue)
