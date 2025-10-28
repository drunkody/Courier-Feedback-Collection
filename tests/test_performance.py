"""Performance and load tests."""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance tests for the application."""

    def test_bulk_feedback_creation(self, api_client, sample_courier):
        """Test creating multiple feedback entries."""
        count = 100
        start_time = time.time()

        for i in range(count):
            feedback_data = {
                "order_id": f"PERF_{i}",
                "courier_id": sample_courier.id,
                "rating": (i % 5) + 1,
                "comment": f"Test feedback {i}",
                "reasons": ["Punctuality"],
                "publish_consent": True
            }
            response = api_client.post("/api/feedback", json=feedback_data)
            assert response.status_code == 200

        duration = time.time() - start_time
        avg_time = duration / count

        print(f"\nCreated {count} feedback in {duration:.2f}s")
        print(f"Average: {avg_time*1000:.2f}ms per request")

        # Should complete in reasonable time
        assert duration < 30  # 30 seconds for 100 items

    def test_concurrent_submissions(self, api_client, sample_courier):
        """Test concurrent feedback submissions."""
        num_threads = 10
        submissions_per_thread = 5

        def submit_feedback(thread_id, submission_id):
            feedback_data = {
                "order_id": f"CONCURRENT_{thread_id}_{submission_id}",
                "courier_id": sample_courier.id,
                "rating": 5,
                "reasons": [],
                "publish_consent": True
            }
            return api_client.post("/api/feedback", json=feedback_data)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(submit_feedback, thread_id, sub_id)
                for thread_id in range(num_threads)
                for sub_id in range(submissions_per_thread)
            ]

            results = [future.result() for future in as_completed(futures)]

        duration = time.time() - start_time
        total_requests = num_threads * submissions_per_thread

        print(f"\nCompleted {total_requests} concurrent requests in {duration:.2f}s")
        print(f"Throughput: {total_requests/duration:.2f} req/s")

        # All should succeed
        assert all(r.status_code == 200 for r in results)

    def test_queue_processing_performance(self):
        """Test queue processing performance."""
        from app.utils import QueueManager

        queue = []
        num_items = 1000

        start_time = time.time()

        # Add items
        for i in range(num_items):
            item = {"order_id": f"QUEUE_{i}", "rating": 5}
            queue = QueueManager.add_to_queue(queue, item, max_size=num_items)

        add_duration = time.time() - start_time

        # Remove items
        start_time = time.time()
        for i in range(num_items):
            item = {"order_id": f"QUEUE_{i}"}
            queue = QueueManager.remove_from_queue(queue, item)

        remove_duration = time.time() - start_time

        print(f"\nQueue operations for {num_items} items:")
        print(f"Add: {add_duration:.3f}s ({num_items/add_duration:.0f} ops/s)")
        print(f"Remove: {remove_duration:.3f}s ({num_items/remove_duration:.0f} ops/s)")

        assert add_duration < 1.0  # Should be fast
        assert len(queue) == 0
