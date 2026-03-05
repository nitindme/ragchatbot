from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import os
import tempfile
import uuid
from app.core.database import get_db
from app.core.security import verify_token
from app.core.config import settings
from app.models.models import Document as DBDocument
from app.services.document_service import DocumentService

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()
document_service = DocumentService()

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
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    """Upload and process a new document"""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
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
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Extract text
        text = document_service.load_document(tmp_path, file_ext)
        print(f"DEBUG: Extracted text length: {len(text)}")
        print(f"DEBUG: First 200 chars: {text[:200] if text else 'EMPTY'}")
        
        # Chunk document
        chunks = document_service.chunk_document(text)
        print(f"DEBUG: Created {len(chunks)} chunks")
        
        # Validate chunks
        if not chunks or len(chunks) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the document"
            )
        
        # Create document record
        doc_id = str(uuid.uuid4())
        db_doc = DBDocument(
            id=doc_id,
            filename=file.filename,
            content_hash=content_hash
        )
        db.add(db_doc)
        db.commit()
        
        # Store embeddings with filename for citations
        document_service.store_embeddings(doc_id, chunks, file.filename)
        
        return {
            "id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "message": "Document uploaded successfully"
        }
    
    finally:
        # Cleanup temp file
        os.unlink(tmp_path)

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
    """List all documents"""
    docs = db.query(DBDocument).all()
    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "created_at": doc.created_at.isoformat()
        }
        for doc in docs
    ]
