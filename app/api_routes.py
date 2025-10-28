import reflex as rx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import Courier, Feedback, engine
import json
import logging


async def get_feedback_by_id(feedback_id: int):
    with Session(engine) as session:
        feedback = session.get(Feedback, feedback_id)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback


async def get_courier_by_id(courier_id: int):
    with Session(engine) as session:
        courier = session.get(Courier, courier_id)
        if not courier:
            raise HTTPException(status_code=404, detail="Courier not found")
        return courier


async def create_feedback(feedback_data: dict):
    try:
        with Session(engine) as session:
            order_id = feedback_data.get("order_id")
            existing_feedback = session.exec(
                select(Feedback).where(Feedback.order_id == order_id)
            ).first()
            if existing_feedback:
                raise HTTPException(
                    status_code=409, detail="Feedback for this order already exists."
                )
            needs_follow_up = feedback_data.get("rating", 0) <= 4
            new_feedback = Feedback(
                order_id=order_id,
                courier_id=feedback_data.get("courier_id"),
                rating=feedback_data.get("rating"),
                comment=feedback_data.get("comment"),
                reasons=json.dumps(feedback_data.get("reasons", [])),
                publish_consent=feedback_data.get("publish_consent", False),
                needs_follow_up=needs_follow_up,
            )
            session.add(new_feedback)
            session.commit()
            session.refresh(new_feedback)
            return new_feedback
    except Exception as e:
        logging.exception(f"Error creating feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def list_feedback(courier_id: int | None = None):
    with Session(engine) as session:
        query = select(Feedback)
        if courier_id:
            query = query.where(Feedback.courier_id == courier_id)
        feedbacks = session.exec(query).all()
        return feedbacks