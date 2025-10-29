"""Integration tests for complete workflows."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestFeedbackSubmissionFlow:
    """Test complete feedback submission workflow."""

    def test_complete_feedback_flow(self, api_client, sample_courier):
        """Test end-to-end feedback submission."""
        # 1. Create feedback
        feedback_data = {
            "order_id": "FLOW001",
            "courier_id": sample_courier.id,
            "rating": 5,
            "comment": "Perfect delivery!",
            "reasons": ["Punctuality", "Politeness"],
            "publish_consent": True
        }

        create_response = api_client.post("/api/feedback", json=feedback_data)
        assert create_response.status_code == status.HTTP_200_OK
        feedback_id = create_response.json()["id"]

        # 2. Retrieve feedback
        get_response = api_client.get(f"/api/feedback/{feedback_id}")
        assert get_response.status_code == status.HTTP_200_OK
        feedback = get_response.json()

        assert feedback["order_id"] == "FLOW001"
        assert feedback["rating"] == 5
        assert feedback["needs_follow_up"] is False

        # 3. List all feedback (should include our new one)
        list_response = api_client.get("/api/feedback")
        assert list_response.status_code == status.HTTP_200_OK
        all_feedback = list_response.json()

        assert any(f["id"] == feedback_id for f in all_feedback)

    def test_low_rating_followup_workflow(self, api_client, sample_courier):
        """Test workflow for low rating requiring follow-up."""
        # Submit low rating
        feedback_data = {
            "order_id": "LOW_RATING_001",
            "courier_id": sample_courier.id,
            "rating": 2,
            "comment": "Late delivery",
            "reasons": [],
            "publish_consent": False
        }

        response = api_client.post("/api/feedback", json=feedback_data)
        assert response.status_code == status.HTTP_200_OK

        feedback = response.json()
        assert feedback["needs_follow_up"] is True
        assert feedback["rating"] == 2


@pytest.mark.integration
class TestCourierWorkflow:
    """Test courier-related workflows."""

    def test_courier_with_multiple_feedback(self, api_client, db_session, sample_courier):
        """Test courier with multiple feedback entries."""
        # Create multiple feedback for same courier
        for i in range(3):
            feedback_data = {
                "order_id": f"MULTI_{i}",
                "courier_id": sample_courier.id,
                "rating": 5 - i,
                "reasons": [],
                "publish_consent": True
            }
            response = api_client.post("/api/feedback", json=feedback_data)
            assert response.status_code == status.HTTP_200_OK

        # Get courier's feedback
        response = api_client.get(f"/api/feedback?courier_id={sample_courier.id}")
        assert response.status_code == status.HTTP_200_OK

        feedback_list = response.json()
        assert len(feedback_list) >= 3
        assert all(f["courier_id"] == sample_courier.id for f in feedback_list)
