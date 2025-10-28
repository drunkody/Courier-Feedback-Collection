"""Tests for state management."""
import pytest
import asyncio
from app.states.feedback_state import FeedbackState


def test_feedback_state_initialization():
    """Test that the feedback state initializes correctly."""
    state = FeedbackState()
    assert state.rating == 0
    assert state.comment == ""
    assert state.reasons == []
    assert state.publish_consent is False


def test_feedback_state_set_rating():
    """Test setting the rating in the feedback state."""
    state = FeedbackState()
    state.set_rating(5)
    assert state.rating == 5


def test_feedback_state_set_comment():
    """Test setting the comment in the feedback state."""
    state = FeedbackState()
    state.set_comment("Great service!")
    assert state.comment == "Great service!"


def test_feedback_state_toggle_reason():
    """Test toggling a reason in the feedback state."""
    state = FeedbackState()
    state.toggle_reason("Punctuality")
    assert "Punctuality" in state.reasons
    state.toggle_reason("Punctuality")
    assert "Punctuality" not in state.reasons


@pytest.mark.asyncio
async def test_feedback_state_submit_feedback_success(mocker):
    """Test successful feedback submission."""
    state = FeedbackState()
    state.order_id = "TEST_ORDER"
    state.courier_id = 123
    state.rating = 5
    state.comment = "Excellent!"

    # Mock the database session and execute
    mock_session = mocker.MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    mocker.patch("sqlmodel.Session", return_value=mocker.MagicMock(__enter__=mocker.MagicMock(return_value=mock_session)))

    await state.do_async(state.submit_feedback)
    assert state.submission_status == "success"


@pytest.mark.asyncio
async def test_feedback_state_submit_feedback_offline(mocker):
    """Test offline feedback submission."""
    state = FeedbackState()
    state.order_id = "TEST_ORDER_OFFLINE"
    state.courier_id = 123
    state.rating = 4
    state.comment = "Good"
    state.is_online = False

    await state.do_async(state.submit_feedback)
    assert state.submission_status == "queued"
    assert len(state.pending_queue) == 1


from app.states.admin_state import AdminState

def test_admin_state_initialization():
    """Test that the admin state initializes correctly."""
    state = AdminState()
    assert state.username == ""
    assert state.password == ""
    assert state.is_authenticated is False
    assert state.error_message == ""
