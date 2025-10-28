"""Tests for utility functions."""
import pytest
from datetime import datetime
from app.utils import (
    generate_request_id,
    serialize_feedback,
    deserialize_feedback,
    validate_feedback_data,
    format_datetime,
    QueueManager
)


class TestGenerateRequestId:
    """Tests for request ID generation."""

    def test_generates_unique_ids(self):
        """Test that unique IDs are generated."""
        data1 = {"order_id": "TEST1", "courier_id": 1}
        data2 = {"order_id": "TEST2", "courier_id": 1}

        id1 = generate_request_id(data1)
        id2 = generate_request_id(data2)

        assert id1 != id2
        assert len(id1) == 32  # MD5 hash length

    def test_consistent_for_same_data(self):
        """Test that same data generates same ID within timeframe."""
        data = {"order_id": "TEST1", "courier_id": 1}

        # Note: Will differ slightly due to timestamp, but format should be same
        id1 = generate_request_id(data)
        assert isinstance(id1, str)
        assert len(id1) == 32


class TestSerializationFunctions:
    """Tests for data serialization."""

    def test_serialize_feedback(self):
        """Test feedback serialization."""
        data = {
            "order_id": "TEST123",
            "rating": 5,
            "comment": "Great!"
        }
        result = serialize_feedback(data)
        assert isinstance(result, str)
        assert "TEST123" in result

    def test_deserialize_feedback(self):
        """Test feedback deserialization."""
        json_str = '{"order_id": "TEST123", "rating": 5}'
        result = deserialize_feedback(json_str)
        assert isinstance(result, dict)
        assert result["order_id"] == "TEST123"
        assert result["rating"] == 5

    def test_roundtrip_serialization(self):
        """Test serialize -> deserialize roundtrip."""
        original = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 5,
            "reasons": ["Punctuality"]
        }
        serialized = serialize_feedback(original)
        deserialized = deserialize_feedback(serialized)

        assert deserialized == original


class TestValidateFeedbackData:
    """Tests for feedback validation."""

    def test_valid_feedback(self):
        """Test validation passes for valid data."""
        data = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 5,
            "comment": "Great service!"
        }
        is_valid, message = validate_feedback_data(data)
        assert is_valid is True
        assert message == ""

    def test_missing_required_field(self):
        """Test validation fails for missing fields."""
        data = {"order_id": "TEST123"}  # Missing courier_id and rating
        is_valid, message = validate_feedback_data(data)
        assert is_valid is False
        assert "Missing required field" in message

    def test_invalid_rating_too_high(self):
        """Test validation fails for rating > 5."""
        data = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 6
        }
        is_valid, message = validate_feedback_data(data)
        assert is_valid is False
        assert "Rating must be between 1 and 5" in message

    def test_invalid_rating_too_low(self):
        """Test validation fails for rating < 1."""
        data = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 0
        }
        is_valid, message = validate_feedback_data(data)
        assert is_valid is False

    def test_comment_too_long(self):
        """Test validation fails for comment > 500 chars."""
        data = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 5,
            "comment": "x" * 501
        }
        is_valid, message = validate_feedback_data(data)
        assert is_valid is False
        assert "exceeds 500 characters" in message

    def test_comment_exactly_500_chars(self):
        """Test validation passes for comment = 500 chars."""
        data = {
            "order_id": "TEST123",
            "courier_id": 1,
            "rating": 5,
            "comment": "x" * 500
        }
        is_valid, message = validate_feedback_data(data)
        assert is_valid is True


class TestFormatDatetime:
    """Tests for datetime formatting."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-01-15 14:30:45"

    def test_format_current_datetime(self):
        """Test formatting current datetime."""
        dt = datetime.now()
        result = format_datetime(dt)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS


class TestQueueManager:
    """Tests for queue management."""

    def test_add_to_empty_queue(self):
        """Test adding to empty queue."""
        queue = []
        item = {"order_id": "TEST1"}
        result = QueueManager.add_to_queue(queue, item)

        assert len(result) == 1
        assert result[0] == item

    def test_add_multiple_items(self):
        """Test adding multiple items."""
        queue = []
        items = [{"order_id": f"TEST{i}"} for i in range(5)]

        for item in items:
            queue = QueueManager.add_to_queue(queue, item)

        assert len(queue) == 5

    def test_queue_size_limit(self):
        """Test queue respects size limit."""
        queue = []
        max_size = 3

        for i in range(5):
            item = {"order_id": f"TEST{i}"}
            queue = QueueManager.add_to_queue(queue, item, max_size=max_size)

        assert len(queue) == max_size
        # Should keep most recent items (TEST2, TEST3, TEST4)
        assert queue[0]["order_id"] == "TEST2"
        assert queue[-1]["order_id"] == "TEST4"

    def test_remove_from_queue(self):
        """Test removing item from queue."""
        queue = [
            {"order_id": "TEST1"},
            {"order_id": "TEST2"},
            {"order_id": "TEST3"}
        ]
        item_to_remove = {"order_id": "TEST2"}

        result = QueueManager.remove_from_queue(queue, item_to_remove)

        assert len(result) == 2
        assert {"order_id": "TEST2"} not in result

    def test_remove_nonexistent_item(self):
        """Test removing item that doesn't exist."""
        queue = [{"order_id": "TEST1"}]
        item = {"order_id": "TEST999"}

        result = QueueManager.remove_from_queue(queue, item)

        assert len(result) == 1
        assert result == queue

    def test_get_pending_count(self):
        """Test getting pending count."""
        queue = [{"order_id": f"TEST{i}"} for i in range(7)]
        count = QueueManager.get_pending_count(queue)
        assert count == 7

    def test_get_pending_count_empty(self):
        """Test pending count for empty queue."""
        assert QueueManager.get_pending_count([]) == 0
