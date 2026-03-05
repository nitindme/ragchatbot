from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import os
import tempfile
import uuid
import shutil
from pathlib import Path
from app.core.database import get_db
from app.core.security import verify_token
from app.core.config import settings
from app.models.models import Document as DBDocument
from app.services.document_service import DocumentService

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()
document_service = DocumentService()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("/app/uploads") if os.path.exists("/app") else Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return payload

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    """Upload document and process in background"""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Compute hash
    content_hash = document_service.compute_file_hash(content)
    
    # Check for duplicates
    existing = db.query(DBDocument).filter(DBDocument.content_hash == content_hash).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already exists (duplicate content)"
        )
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Save file to storage
    file_path = UPLOAD_DIR / f"{doc_id}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record with pending status
    db_doc = DBDocument(
        id=doc_id,
        filename=file.filename,
        content_hash=content_hash,
        file_path=str(file_path),
        file_size=file_size,
        status='pending'  # Will be processed in background
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Trigger background processing
    if background_tasks:
        from app.services.background_processor import background_processor
        if background_processor:
            background_tasks.add_task(background_processor.process_document, db, db_doc)
    
    return {
        "id": doc_id,
        "filename": file.filename,
        "status": "pending",
        "message": "Document uploaded successfully. Processing in background...",
        "file_size": file_size
    }

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    """Delete a document and its embeddings"""
    doc = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete embeddings from ChromaDB
    document_service.delete_embeddings(document_id)
    
    # Delete from database
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.get("/documents")
def list_documents(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    """List all documents with processing status"""
    docs = db.query(DBDocument).order_by(DBDocument.created_at.desc()).all()
    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "status": doc.status,
            "file_size": doc.file_size,
            "total_chunks": doc.total_chunks,
            "page_count": doc.page_count,
            "processing_error": doc.processing_error,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
        }
        for doc in docs
    ]
