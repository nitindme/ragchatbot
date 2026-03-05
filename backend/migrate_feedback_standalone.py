#!/usr/bin/env python3
"""
Standalone migration script to change feedback.message_id from INTEGER to VARCHAR
"""
import psycopg2
import os

def run_migration():
    # Database connection parameters
    db_params = {
        'dbname': os.getenv('POSTGRES_DB', 'ragchatbot'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'host': os.getenv('POSTGRES_HOST', 'db'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }
    
    conn = None
    try:
        # Connect to database
        print(f"Connecting to database: {db_params['dbname']}@{db_params['host']}...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Check if feedback table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'feedback'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Feedback table does not exist yet. No migration needed.")
            return
        
        # Check current column type
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'feedback' AND column_name = 'message_id';
        """)
        result = cursor.fetchone()
        
        if not result:
            print("❌ message_id column not found in feedback table")
            return
            
        current_type = result[0]
        print(f"Current message_id type: {current_type}")
        
        if current_type in ('character varying', 'varchar', 'text'):
            print("✅ message_id is already a string type. No migration needed.")
            return
        
        # Perform migration
        print("Running migration: ALTER TABLE feedback ALTER COLUMN message_id TYPE VARCHAR...")
        cursor.execute("""
            ALTER TABLE feedback 
            ALTER COLUMN message_id TYPE VARCHAR 
            USING message_id::VARCHAR;
        """)
        
        # Verify the change
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'feedback' AND column_name = 'message_id';
        """)
        new_type = cursor.fetchone()[0]
        
        # Commit transaction
        conn.commit()
        print(f"✅ Migration successful! message_id type changed from {current_type} to {new_type}")
        
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
