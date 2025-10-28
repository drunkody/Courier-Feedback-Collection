"""Utility functions and helpers."""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple


def generate_request_id(data: Dict[str, Any]) -> str:
    """
    Generate unique ID for feedback submission.

    Args:
        data: Feedback data containing order_id and courier_id

    Returns:
        MD5 hash string
    """
    unique_string = f"{data.get('order_id')}_{data.get('courier_id')}_{datetime.utcnow().isoformat()}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def serialize_feedback(data: Dict[str, Any]) -> str:
    """
    Serialize feedback data for storage.

    Args:
        data: Feedback dictionary

    Returns:
        JSON string
    """
    return json.dumps(data, default=str)


def deserialize_feedback(data: str) -> Dict[str, Any]:
    """
    Deserialize feedback data from storage.

    Args:
        data: JSON string

    Returns:
        Feedback dictionary
    """
    return json.loads(data)


def validate_feedback_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate feedback data structure.

    Args:
        data: Feedback data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
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
    """
    Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class QueueManager:
    """Manage local storage queue operations."""

    @staticmethod
    def add_to_queue(queue: List[dict], item: dict, max_size: int = 50) -> List[dict]:
        """
        Add item to queue with size limit (FIFO).

        Args:
            queue: Current queue list
            item: Item to add
            max_size: Maximum queue size

        Returns:
            Updated queue list
        """
        # Create new list to avoid mutation issues
        new_queue = queue.copy()

        if len(new_queue) >= max_size:
            # Remove oldest item (FIFO)
            new_queue.pop(0)

        new_queue.append(item)
        return new_queue

    @staticmethod
    def remove_from_queue(queue: List[dict], item: dict) -> List[dict]:
        """
        Remove item from queue by matching order_id.

        Args:
            queue: Current queue list
            item: Item with order_id to remove

        Returns:
            Updated queue list
        """
        return [q for q in queue if q.get("order_id") != item.get("order_id")]

    @staticmethod
    def get_pending_count(queue: List[dict]) -> int:
        """
        Get count of pending items.

        Args:
            queue: Queue list

        Returns:
            Number of items in queue
        """
        return len(queue)

    @staticmethod
    def clear_queue(queue: List[dict]) -> List[dict]:
        """
        Clear all items from queue.

        Returns:
            Empty list
        """
        return []
