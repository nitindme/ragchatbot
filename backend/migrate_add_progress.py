"""
Migration script to add processing_progress column to documents table
"""
import psycopg2
import os

def migrate():
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://rag:rag@postgres:5432/ragdb')
    
    # Connect to the database
    conn = psycopg2.connect(database_url)
    
    try:
        cursor = conn.cursor()
        
        # Add processing_progress column
        print("Adding processing_progress column...")
        cursor.execute("""
            ALTER TABLE documents 
            ADD COLUMN IF NOT EXISTS processing_progress INTEGER DEFAULT 0 NOT NULL;
        """)
        
        # Set progress to 100 for completed documents
        print("Setting progress to 100 for completed documents...")
        cursor.execute("""
            UPDATE documents 
            SET processing_progress = 100 
            WHERE status = 'completed';
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
