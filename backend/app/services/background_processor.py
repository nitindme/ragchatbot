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
        
    async def process_pending_documents(self):
        """Process all pending documents in the queue"""
        if self.processing:
            logger.info("Already processing documents, skipping...")
            return
            
        self.processing = True
        db = SessionLocal()
        
        try:
            # Get all pending documents
            pending_docs = db.query(Document).filter(
                Document.status == 'pending'
            ).order_by(Document.created_at).all()
            
            logger.info(f"Found {len(pending_docs)} pending documents to process")
            
            for doc in pending_docs:
                await self.process_document(db, doc)
                # Yield to event loop after each document to allow API requests
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in background processor: {str(e)}")
        finally:
            db.close()
            self.processing = False
            
    async def process_document(self, db: Session, doc: Document):
        """Process a single document"""
        try:
            logger.info(f"Processing document: {doc.filename} (ID: {doc.id})")
            
            # Update status to processing
            doc.status = 'processing'
            db.commit()
            
            # Read the file from storage
            if not doc.file_path or not Path(doc.file_path).exists():
                raise FileNotFoundError(f"File not found: {doc.file_path}")
            
            with open(doc.file_path, 'rb') as f:
                file_content = f.read()
            
            # Process with Docling and create embeddings
            logger.info(f"Starting OCR and chunking for {doc.filename}...")
            
            # Yield to event loop before heavy processing
            await asyncio.sleep(0)
            
            result = await asyncio.to_thread(
                self.document_service.process_pdf,
                file_content,
                doc.filename,
                str(doc.id)
            )
            
            # Yield to event loop after heavy processing
            await asyncio.sleep(0)
            
            # Update document with results
            doc.status = 'completed'
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
        
    logger.info("Starting background document processor...")
    
    while True:
        try:
            await background_processor.process_pending_documents()
        except Exception as e:
            logger.error(f"Error in background processor loop: {str(e)}")
        
        # Wait 30 seconds before checking for new documents
        await asyncio.sleep(30)
