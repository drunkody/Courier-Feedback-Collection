"""FastAPI route handlers."""
from typing import Optional
from fastapi import APIRouter, Query

from app.services import FeedbackService, CourierService

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/feedback")
async def create_feedback(feedback_data: dict):
    """Create new feedback entry."""
    return FeedbackService.create_feedback(feedback_data)


@router.get("/feedback/{feedback_id}")
async def get_feedback(feedback_id: int):
    """Get feedback by ID."""
    return FeedbackService.get_feedback(feedback_id)


@router.get("/feedback")
async def list_feedback(courier_id: Optional[int] = Query(None)):
    """List feedback, optionally filtered by courier."""
    return FeedbackService.list_feedback(courier_id)


@router.get("/courier/{courier_id}")
async def get_courier(courier_id: int):
    """Get courier information."""
    return CourierService.get_courier(courier_id)
