from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    message_id = Column(String, nullable=False)  # Changed from Integer to String for UUID
    
    # User's question
    question = Column(Text, nullable=False)
    
    # Bot's response
    response = Column(Text, nullable=False)
    
    # Retrieved chunks that were used
    retrieved_chunks = Column(JSON, nullable=True)
    
    # Source documents
    sources = Column(JSON, nullable=True)
    
    # Feedback (1 = thumbs up, -1 = thumbs down, 0 = neutral)
    rating = Column(Integer, nullable=False)
    
    # Optional user comment
    comment = Column(Text, nullable=True)
    
    # Metadata
    is_reviewed = Column(Boolean, default=False)
    is_used_for_training = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, session={self.session_id}, rating={self.rating})>"
