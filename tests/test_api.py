"""Tests for API endpoints."""
import pytest
from fastapi import status


@pytest.mark.api
@pytest.mark.unit
class TestFeedbackEndpoints:
    """Tests for feedback API endpoints."""

    def test_create_feedback_success(self, api_client, sample_courier, mock_feedback_data):
        """Test POST /api/feedback success."""
        mock_feedback_data["courier_id"] = sample_courier.id

        response = api_client.post("/api/feedback", json=mock_feedback_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["order_id"] == mock_feedback_data["order_id"]
        assert data["rating"] == mock_feedback_data["rating"]

    def test_create_feedback_duplicate(self, api_client, sample_feedback):
        """Test creating duplicate feedback."""
        duplicate_data = {
            "order_id": sample_feedback.order_id,
            "courier_id": sample_feedback.courier_id,
            "rating": 5,
            "reasons": [],
            "publish_consent": False
        }

        response = api_client.post("/api/feedback", json=duplicate_data)

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_get_feedback_by_id_success(self, api_client, sample_feedback):
        """Test GET /api/feedback/{id} success."""
        response = api_client.get(f"/api/feedback/{sample_feedback.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_feedback.id
        assert data["order_id"] == sample_feedback.order_id

    def test_get_feedback_not_found(self, api_client):
        """Test GET /api/feedback/{id} not found."""
        response = api_client.get("/api/feedback/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_feedback_all(self, api_client, sample_feedback):
        """Test GET /api/feedback list all."""
        response = api_client.get("/api/feedback")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_feedback_filter_by_courier(self, api_client, sample_courier, sample_feedback):
        """Test GET /api/feedback with courier filter."""
        response = api_client.get(f"/api/feedback?courier_id={sample_courier.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(item["courier_id"] == sample_courier.id for item in data)


@pytest.mark.api
@pytest.mark.unit
class TestCourierEndpoints:
    """Tests for courier API endpoints."""

    def test_get_courier_success(self, api_client, sample_courier):
        """Test GET /api/courier/{id} success."""
        response = api_client.get(f"/api/courier/{sample_courier.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_courier.id
        assert data["name"] == sample_courier.name

    def test_get_courier_not_found(self, api_client):
        """Test GET /api/courier/{id} not found."""
        response = api_client.get("/api/courier/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
