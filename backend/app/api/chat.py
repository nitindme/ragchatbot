from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uuid
import json
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.models import ChatSession, ChatMessage
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()

class ChatRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    role: str
    message_id: str
    sources: list = []
    retrieved_chunks: list = []

@router.post("/start")
@limiter.limit("10/minute")
def start_chat_session(request: Request, db: Session = Depends(get_db)):
    """Start a new chat session"""
    session = ChatSession(id=str(uuid.uuid4()))
    db.add(session)
    db.commit()
    
    return {"session_id": str(session.id)}

@router.post("/{session_id}/message", response_model=ChatMessageResponse)
@limiter.limit("20/minute")
def send_message(
    request: Request,
    session_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get RAG response"""
    # Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get chat history
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    chat_history = [
        {"role": msg.role, "message": msg.message}
        for msg in messages
    ]
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        message=chat_request.message
    )
    db.add(user_msg)
    db.flush()  # Get the message ID
    
    # Generate response with metadata
    result = chat_service.generate_response(chat_request.message, chat_history)
    response_text = result["response"]
    
    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        message=response_text
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    
    return {
        "session_id": session_id,
        "role": "assistant",
        "message": response_text,
        "message_id": str(assistant_msg.id),
        "sources": result.get("sources", []),
        "retrieved_chunks": result.get("retrieved_chunks", [])
    }

@router.get("/{session_id}/history")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "message": msg.message,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }

@router.get("/sessions")
@limiter.limit("30/minute")
def list_sessions(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 20
):
    """List recent chat sessions"""
    sessions = db.query(ChatSession).order_by(
        ChatSession.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": str(session.id),
            "created_at": session.created_at.isoformat(),
            "message_count": len(session.messages)
        }
        for session in sessions
    ]

@router.delete("/{session_id}")
@limiter.limit("10/minute")
def delete_session(
    request: Request,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

@router.post("/{session_id}/stream")
@limiter.limit("20/minute")
async def send_message_stream(
    request: Request,
    session_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get streaming RAG response"""
    # Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get chat history
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    chat_history = [
        {"role": msg.role, "message": msg.message}
        for msg in messages
    ]
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        message=chat_request.message
    )
    db.add(user_msg)
    db.commit()
    
    async def generate():
        full_response = ""
        try:
            # Generate response
            response_text = chat_service.generate_response(chat_request.message, chat_history)
            
            # Stream word by word
            words = response_text.split()
            for word in words:
                full_response += word + " "
                yield f"data: {json.dumps({'text': word + ' '})}\n\n"
            
            # Save assistant message
            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                message=full_response.strip()
            )
            db.add(assistant_msg)
            db.commit()
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

