"""
Script to reprocess existing documents and embed them into ChromaDB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Override URLs to use localhost instead of Docker hostnames
os.environ['CHROMA_URL'] = 'http://localhost:8001'
os.environ['DATABASE_URL'] = 'postgresql://rag:rag@localhost:5432/ragdb'

from app.core.database import SessionLocal
from app.models.models import Document
from app.services.document_service import DocumentService
from app.core.config import settings

def reprocess_documents():
    db = SessionLocal()
    doc_service = DocumentService()
    
    try:
        # Get all documents from database
        documents = db.query(Document).all()
        print(f"Found {len(documents)} documents to reprocess")
        
        for doc in documents:
            print(f"\nReprocessing: {doc.filename}")
            print(f"  File path: {doc.file_path}")
            
            if not os.path.exists(doc.file_path):
                print(f"  ❌ File not found: {doc.file_path}")
                continue
            
            try:
                # Load and chunk the document
                print(f"  Loading document...")
                text_chunks = doc_service.load_and_chunk_document(doc.file_path)
                print(f"  ✓ Created {len(text_chunks)} chunks")
                
                # Store in ChromaDB
                print(f"  Storing in vector database...")
                doc_service.store_embeddings(doc.id, text_chunks)
                print(f"  ✓ Embedded into ChromaDB")
                
            except Exception as e:
                print(f"  ❌ Error processing document: {str(e)}")
                continue
        
        print(f"\n✅ Reprocessing complete!")
        
        # Verify
        print(f"\nVerifying ChromaDB...")
        collection_count = doc_service.collection.count()
        print(f"  Total embeddings in ChromaDB: {collection_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reprocess_documents()
