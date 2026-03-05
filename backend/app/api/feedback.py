from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.feedback import Feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackCreate(BaseModel):
    session_id: str
    message_id: int
    question: str
    response: str
    retrieved_chunks: Optional[List[dict]] = None
    sources: Optional[List[str]] = None
    rating: int  # 1 = thumbs up, -1 = thumbs down
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    session_id: str
    message_id: int
    question: str
    response: str
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Submit user feedback (thumbs up/down) for a bot response"""
    
    # Create feedback record
    db_feedback = Feedback(
        session_id=feedback.session_id,
        message_id=feedback.message_id,
        question=feedback.question,
        response=feedback.response,
        retrieved_chunks=feedback.retrieved_chunks,
        sources=feedback.sources,
        rating=feedback.rating,
        comment=feedback.comment
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return db_feedback

@router.get("/negative", response_model=List[FeedbackResponse])
def get_negative_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all thumbs down feedback for review"""
    feedbacks = db.query(Feedback).filter(
        Feedback.rating == -1
    ).order_by(
        Feedback.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return feedbacks

@router.get("/unreviewed", response_model=List[FeedbackResponse])
def get_unreviewed_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all unreviewed feedback"""
    feedbacks = db.query(Feedback).filter(
        Feedback.is_reviewed == False
    ).order_by(
        Feedback.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return feedbacks

@router.patch("/{feedback_id}/review")
def mark_feedback_reviewed(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """Mark feedback as reviewed"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.is_reviewed = True
    feedback.reviewed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Feedback marked as reviewed"}

@router.get("/stats")
def get_feedback_stats(db: Session = Depends(get_db)):
    """Get feedback statistics"""
    total = db.query(Feedback).count()
    positive = db.query(Feedback).filter(Feedback.rating == 1).count()
    negative = db.query(Feedback).filter(Feedback.rating == -1).count()
    unreviewed = db.query(Feedback).filter(Feedback.is_reviewed == False).count()
    
    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "unreviewed": unreviewed,
        "satisfaction_rate": round((positive / total * 100) if total > 0 else 0, 2)
    }

@router.get("/all", response_model=List[FeedbackResponse])
def get_all_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all feedback for admin review"""
    feedbacks = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).offset(skip).limit(limit).all()
    return feedbacks
