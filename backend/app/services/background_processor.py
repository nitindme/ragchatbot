"""
Background task processor for document OCR and embedding
"""
import asyncio
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """Handles background processing of documents"""
    
    def __init__(self, document_service=None):
        self.document_service = document_service
        self.processing = False
        
    def reset_stuck_documents(self):
        """Reset documents stuck in 'processing' status back to 'pending'"""
        db = SessionLocal()
        try:
            stuck_docs = db.query(Document).filter(
                Document.status == 'processing'
            ).all()
            
            if stuck_docs:
                logger.info(f"Found {len(stuck_docs)} stuck documents, resetting to pending...")
                for doc in stuck_docs:
                    doc.status = 'pending'
                    doc.processing_progress = 0
                db.commit()
                logger.info(f"✅ Reset {len(stuck_docs)} documents to pending")
        except Exception as e:
            logger.error(f"Error resetting stuck documents: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
    async def process_pending_documents(self):
        """Process all pending documents in the queue"""
        if self.processing:
            logger.info("Already processing documents, skipping...")
            return
            
        self.processing = True
        db = None
        
        try:
            # Create a new database session for this background task
            db = SessionLocal()
            
            # Get all pending documents
            pending_docs = db.query(Document).filter(
                Document.status == 'pending'
            ).order_by(Document.created_at).all()
            
            logger.info(f"Found {len(pending_docs)} pending documents to process")
            
            for doc in pending_docs:
                # Create a fresh session for each document to avoid blocking
                doc_db = SessionLocal()
                try:
                    await self.process_document(doc_db, doc)
                finally:
                    doc_db.close()
                    # Yield to event loop after each document
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in background processor: {str(e)}")
        finally:
            if db:
                db.close()
            self.processing = False
            
    async def process_document(self, db: Session, doc: Document):
        """Process a single document"""
        try:
            # Re-fetch the document to ensure we have fresh data in this session
            doc = db.query(Document).filter(Document.id == doc.id).first()
            if not doc or doc.status != 'pending':
                logger.info(f"Document {doc.id if doc else 'unknown'} no longer pending, skipping")
                return
                
            logger.info(f"▶️  Processing document: {doc.filename} (ID: {doc.id})")
            logger.info(f"   File: {doc.file_path}, Size: {doc.file_size / 1024:.2f} KB")
            
            # Update status to processing
            doc.status = 'processing'
            doc.processing_progress = 10  # Started
            db.commit()
            db.refresh(doc)  # Refresh to avoid stale data
            logger.info(f"   Progress: 10% - Processing started")
            
            # Read the file from storage
            if not doc.file_path or not Path(doc.file_path).exists():
                raise FileNotFoundError(f"File not found: {doc.file_path}")
            
            with open(doc.file_path, 'rb') as f:
                file_content = f.read()
            
            # Process with Docling and create embeddings
            logger.info(f"🚀 Starting OCR and chunking for {doc.filename}...")
            
            # Update progress before heavy processing (combine updates to reduce DB commits)
            doc.processing_progress = 30  # Starting OCR
            db.commit()
            logger.info(f"   Progress: 30% - OCR phase started")
            
            # Create progress callback to update database during OCR
            def update_progress(progress: int):
                """Update document progress in database"""
                try:
                    doc.processing_progress = progress
                    db.commit()
                    logger.info(f"   Progress: {progress}% - OCR in progress")
                except Exception as e:
                    logger.error(f"Failed to update progress: {e}")
            
            result = await asyncio.to_thread(
                self.document_service.process_pdf,
                file_content,
                doc.filename,
                str(doc.id),
                update_progress  # Pass the progress callback
            )
            
            # Update document with results (single commit)
            doc.status = 'completed'
            doc.processing_progress = 100  # Completed
            doc.total_chunks = result.get('total_chunks', 0)
            doc.page_count = result.get('page_count', 0)
            doc.processing_error = None
            db.commit()
            
            logger.info(f"✅ Successfully completed: {doc.filename}")
            logger.info(f"   Progress: 100% - {doc.page_count} pages, {doc.total_chunks} chunks")
            logger.info(f"   Total time: {result.get('processing_time', 0):.2f}s")
            doc.processing_progress = 100  # Completed
            doc.total_chunks = result.get('total_chunks', 0)
            doc.page_count = result.get('page_count', 0)
            doc.processing_error = None
            db.commit()
            
            logger.info(f"✅ Successfully processed {doc.filename}: {doc.total_chunks} chunks, {doc.page_count} pages")
            
        except Exception as e:
            logger.error(f"❌ Failed to process document {doc.filename}: {str(e)}")
            doc.status = 'failed'
            doc.processing_error = str(e)
            db.commit()


# Global processor instance - will be initialized with document_service
background_processor = None


def init_background_processor(document_service):
    """Initialize the background processor with a document service"""
    global background_processor
    background_processor = BackgroundProcessor(document_service)
    return background_processor


async def start_background_processor():
    """Start the background processor loop"""
    if background_processor is None:
        logger.error("Background processor not initialized!")
        return
    
    # Reset any stuck documents on startup
    logger.info("Checking for stuck documents...")
    background_processor.reset_stuck_documents()
        
    logger.info("Starting background document processor...")
    
    while True:
        try:
            await background_processor.process_pending_documents()
        except Exception as e:
            logger.error(f"Error in background processor loop: {str(e)}")
        
        # Wait 30 seconds before checking for new documents
        await asyncio.sleep(30)
