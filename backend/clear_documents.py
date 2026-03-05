"""
Script to clear all documents and embeddings
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Override URLs to use localhost
os.environ['DATABASE_URL'] = 'postgresql://rag:rag@localhost:5432/ragdb'

from app.core.database import SessionLocal
from app.models.models import Document, ChatSession, ChatMessage

def clear_all():
    db = SessionLocal()
    
    try:
        # Delete all chat messages
        msg_count = db.query(ChatMessage).delete()
        print(f"Deleted {msg_count} chat messages")
        
        # Delete all chat sessions
        session_count = db.query(ChatSession).delete()
        print(f"Deleted {session_count} chat sessions")
        
        # Delete all documents
        doc_count = db.query(Document).delete()
        print(f"Deleted {doc_count} documents")
        
        db.commit()
        print("\n✅ All documents and chat history cleared!")
        print("\nNext steps:")
        print("1. Go to http://localhost:3000")
        print("2. Login with admin/admin123")
        print("3. Upload your PDF documents again")
        print("4. The documents will be properly embedded into ChromaDB")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    response = input("This will delete ALL documents and chat history. Continue? (yes/no): ")
    if response.lower() == 'yes':
        clear_all()
    else:
        print("Cancelled")
