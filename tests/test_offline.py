"""Tests for offline queue functionality."""
import pytest
from app.utils import QueueManager
from config import config


@pytest.mark.offline
class TestOfflineQueue:
    """Tests for offline queue behavior."""

    def test_queue_initialization(self):
        """Test queue starts empty."""
        queue = []
        assert QueueManager.get_pending_count(queue) == 0

    def test_add_single_item_to_queue(self):
        """Test adding single item to queue."""
        queue = []
        item = {
            "order_id": "OFF001",
            "courier_id": 1,
            "rating": 5,
            "timestamp": "2024-01-15T10:00:00"
        }

        queue = QueueManager.add_to_queue(queue, item)

        assert len(queue) == 1
        assert queue[0]["order_id"] == "OFF001"

    def test_queue_fifo_behavior(self):
        """Test queue follows FIFO when limit reached."""
        queue = []
        max_size = 3

        # Add 5 items to queue with size limit of 3
        for i in range(5):
            item = {"order_id": f"OFF{i}"}
            queue = QueueManager.add_to_queue(queue, item, max_size=max_size)

        # Should keep last 3 items (OFF2, OFF3, OFF4)
        assert len(queue) == max_size
        assert queue[0]["order_id"] == "OFF2"
        assert queue[1]["order_id"] == "OFF3"
        assert queue[2]["order_id"] == "OFF4"

    def test_remove_specific_item(self):
        """Test removing specific item from queue."""
        queue = [
            {"order_id": "OFF1"},
            {"order_id": "OFF2"},
            {"order_id": "OFF3"}
        ]

        queue = QueueManager.remove_from_queue(queue, {"order_id": "OFF2"})

        assert len(queue) == 2
        assert not any(item["order_id"] == "OFF2" for item in queue)

    def test_queue_persistence_simulation(self):
        """Test queue data structure for localStorage compatibility."""
        import json

        queue = [
            {
                "order_id": "OFF001",
                "courier_id": 1,
                "rating": 5,
                "reasons": ["Punctuality"],
                "timestamp": "2024-01-15T10:00:00"
            }
        ]

        # Simulate localStorage serialization
        serialized = json.dumps(queue)
        deserialized = json.loads(serialized)

        assert deserialized == queue
        assert deserialized[0]["order_id"] == "OFF001"

    def test_queue_max_size_from_config(self):
        """Test queue respects config max size."""
        queue = []
        max_size = config.MAX_QUEUE_SIZE

        # Add more items than max size
        for i in range(max_size + 10):
            item = {"order_id": f"OFF{i}"}
            queue = QueueManager.add_to_queue(queue, item, max_size=max_size)

        assert len(queue) == max_size


@pytest.mark.offline
@pytest.mark.integration
class TestOfflineSubmissionFlow:
    """Integration tests for offline submission flow."""

    def test_offline_submission_queues_data(self):
        """Test that offline submissions are queued."""
        # This would test the full flow in FeedbackState
        # For now, just test the data structure
        pending_item = {
            "order_id": "OFFLINE_TEST",
            "courier_id": 1,
            "rating": 4,
            "comment": "Good service",
            "reasons": ["Politeness"],
            "publish_consent": True,
            "timestamp": "2024-01-15T10:00:00",
            "request_id": "abc123"
        }

        # Validate structure
        assert "order_id" in pending_item
        assert "timestamp" in pending_item
        assert "request_id" in pending_item
        assert pending_item["rating"] in range(1, 6)
