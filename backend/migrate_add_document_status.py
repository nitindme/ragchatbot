#!/usr/bin/env python3
"""
Migration script to add status tracking columns to documents table
"""
import psycopg2
import os

def run_migration():
    # Database connection parameters
    db_params = {
        'dbname': os.getenv('POSTGRES_DB', 'ragdb'),
        'user': os.getenv('POSTGRES_USER', 'rag'),
        'password': os.getenv('POSTGRES_PASSWORD', 'ragpass'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }
    
    conn = None
    try:
        # Connect to database
        print(f"Connecting to database: {db_params['dbname']}@{db_params['host']}...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Check if documents table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Documents table does not exist yet. No migration needed.")
            return
        
        print("Running migration: Adding status tracking columns to documents table...")
        
        # Add new columns
        migrations = [
            ("file_path", "VARCHAR"),
            ("file_size", "INTEGER"),
            ("status", "VARCHAR DEFAULT 'completed'"),  # Set existing docs as completed
            ("processing_error", "TEXT"),
            ("total_chunks", "INTEGER"),
            ("page_count", "INTEGER"),
            ("updated_at", "TIMESTAMP DEFAULT NOW()"),
        ]
        
        for column_name, column_type in migrations:
            # Check if column already exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'documents' AND column_name = %s
                );
            """, (column_name,))
            
            column_exists = cursor.fetchone()[0]
            
            if not column_exists:
                print(f"  Adding column: {column_name} ({column_type})")
                cursor.execute(f"""
                    ALTER TABLE documents 
                    ADD COLUMN {column_name} {column_type};
                """)
            else:
                print(f"  Column {column_name} already exists, skipping")
        
        # Commit transaction
        conn.commit()
        print("✅ Migration successful! Document status tracking columns added.")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
