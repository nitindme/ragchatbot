#!/usr/bin/env python3
"""
Migration script to change feedback.message_id from INTEGER to VARCHAR
Run this once to update the existing database schema
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Check if feedback table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'feedback'
                );
            """))
            
            if not result.scalar():
                print("Feedback table doesn't exist yet. No migration needed.")
                return
            
            # Check current column type
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'feedback' AND column_name = 'message_id';
            """))
            
            current_type = result.scalar()
            
            if current_type == 'character varying' or current_type == 'varchar':
                print("message_id is already VARCHAR. No migration needed.")
                return
            
            print(f"Current message_id type: {current_type}")
            print("Migrating message_id from INTEGER to VARCHAR...")
            
            # Alter the column type
            conn.execute(text("""
                ALTER TABLE feedback 
                ALTER COLUMN message_id TYPE VARCHAR 
                USING message_id::VARCHAR;
            """))
            
            trans.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate()
