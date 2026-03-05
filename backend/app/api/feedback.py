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
    message_id: str  # Changed from int to str to match UUID from chat
    question: str
    response: str
    retrieved_chunks: Optional[List[dict]] = None
    sources: Optional[List[str]] = None
    rating: int  # 1 = thumbs up, -1 = thumbs down
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    session_id: str
    message_id: str  # Changed from int to str
    question: str
    response: str
    rating: int
    comment: Optional[str]
    is_reviewed: bool
    created_at: datetime
    reviewed_at: Optional[datetime]
    sources: Optional[List[str]]
    
    class Config:
        from_attributes = True

class FeedbackDetailResponse(BaseModel):
    id: int
    session_id: str
    message_id: str
    question: str
    response: str
    rating: int
    comment: Optional[str]
    is_reviewed: bool
    created_at: datetime
    reviewed_at: Optional[datetime]
    sources: Optional[List[str]]
    retrieved_chunks: Optional[List[dict]]
    
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
    """Get detailed feedback statistics"""
    from sqlalchemy import func
    
    total = db.query(Feedback).count()
    positive = db.query(Feedback).filter(Feedback.rating == 1).count()
    negative = db.query(Feedback).filter(Feedback.rating == -1).count()
    unreviewed = db.query(Feedback).filter(Feedback.is_reviewed == False).count()
    with_comments = db.query(Feedback).filter(Feedback.comment != None, Feedback.comment != '').count()
    
    # Get feedback count by date (last 7 days)
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_feedback = db.query(Feedback).filter(
        Feedback.created_at >= seven_days_ago
    ).count()
    
    # Average rating
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0
    
    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "unreviewed": unreviewed,
        "with_comments": with_comments,
        "recent_7_days": recent_feedback,
        "average_rating": round(float(avg_rating), 2),
        "satisfaction_rate": round((positive / total * 100) if total > 0 else 0, 2)
    }

@router.get("/all")
def get_all_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all feedback for admin review with detailed information"""
    feedbacks = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": f.id,
            "session_id": f.session_id,
            "message_id": f.message_id,
            "question": f.question[:200] + "..." if len(f.question) > 200 else f.question,
            "response": f.response[:300] + "..." if len(f.response) > 300 else f.response,
            "rating": f.rating,
            "rating_text": "👍 Helpful" if f.rating == 1 else "👎 Not Helpful",
            "comment": f.comment,
            "is_reviewed": f.is_reviewed,
            "created_at": f.created_at.isoformat(),
            "reviewed_at": f.reviewed_at.isoformat() if f.reviewed_at else None,
            "sources": f.sources,
            "has_comment": bool(f.comment and f.comment.strip()),
            "time_ago": _get_time_ago(f.created_at)
        }
        for f in feedbacks
    ]

def _get_time_ago(dt: datetime) -> str:
    """Convert datetime to human-readable time ago format"""
    # Handle timezone-aware datetime
    now = datetime.utcnow()
    if dt.tzinfo is not None:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    return "Just now"
