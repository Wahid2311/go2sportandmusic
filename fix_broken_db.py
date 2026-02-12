#!/usr/bin/env python
"""
Script to fix the broken database state before running migrations.
This script handles both SQLite (local) and PostgreSQL (production).
"""

import os
import sys
from pathlib import Path

def fix_database():
    """Fix the broken database state"""
    
    database_url = os.environ.get('DATABASE_URL')
    db_path = '/app/db.sqlite3'
    
    # Determine if we're using PostgreSQL or SQLite
    if database_url and database_url.startswith('postgres'):
        print("Using PostgreSQL database...")
        fix_postgres_database(database_url)
    elif os.path.exists(db_path):
        print(f"Using SQLite database at {db_path}...")
        fix_sqlite_database(db_path)
    else:
        print("No database found. Will be created by migrations.")
        return


def fix_postgres_database(database_url):
    """Fix the PostgreSQL database"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading /
            user=parsed.username,
            password=parsed.password
        )
        cursor = conn.cursor()
        
        # 1. Delete all broken migration records (including the old 0009 and 0006_placeholder)
        print("Deleting broken migration records...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name = '0006_add_eventcategory_timestamps' OR
                name = '0007_set_default_category' OR
                name = '0009_fix_eventcategory_schema' OR
                name = '0009_fix_null_categories' OR
                name LIKE '0010_%' OR 
                name LIKE '0011_%' OR 
                name LIKE '0012_%' OR 
                name LIKE '0013_%' OR 
                name LIKE '0014_%' OR 
                name LIKE '0015_%' OR 
                name LIKE '0016_%' OR 
                name LIKE '0017_%' OR 
                name LIKE '0018_%' OR 
                name LIKE '0019_%'
            )
        """)
        deleted_count = cursor.rowcount
        print(f"✓ Deleted {deleted_count} broken migration records")
        
        # 2. Check if the EventCategory table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'events_eventcategory'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("Checking EventCategory table schema...")
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'events_eventcategory'
                ORDER BY column_name
            """)
            columns = {row[0] for row in cursor.fetchall()}
            print(f"Current columns: {sorted(columns)}")
            
            # 3. If the table has old columns but not new ones, we need to add them
            if 'created' in columns and 'created_at' not in columns:
                print("Adding new timestamp columns...")
                cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created_at TIMESTAMP")
                cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated_at TIMESTAMP")
                print("✓ Added new timestamp columns")
                
                # Copy data from old columns to new columns
                print("Copying data from old columns to new columns...")
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET created_at = created, updated_at = modified
                """)
                print(f"✓ Copied data ({cursor.rowcount} rows)")
        
        conn.commit()
        conn.close()
        print("✓ PostgreSQL database fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error fixing PostgreSQL database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


def fix_sqlite_database(db_path):
    """Fix the SQLite database"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Delete all broken migration records (including the old 0009 and 0006_placeholder)
        print("Deleting broken migration records...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name = '0006_add_eventcategory_timestamps' OR
                name = '0007_set_default_category' OR
                name = '0009_fix_eventcategory_schema' OR
                name = '0009_fix_null_categories' OR
                name LIKE '0010_%' OR 
                name LIKE '0011_%' OR 
                name LIKE '0012_%' OR 
                name LIKE '0013_%' OR 
                name LIKE '0014_%' OR 
                name LIKE '0015_%' OR 
                name LIKE '0016_%' OR 
                name LIKE '0017_%' OR 
                name LIKE '0018_%' OR 
                name LIKE '0019_%'
            )
        """)
        deleted_count = cursor.rowcount
        print(f"✓ Deleted {deleted_count} broken migration records")
        
        # 2. Check the current EventCategory table schema
        print("Checking EventCategory table schema...")
        cursor.execute("PRAGMA table_info(events_eventcategory)")
        columns = {row[1]: row for row in cursor.fetchall()}
        print(f"Current columns: {list(columns.keys())}")
        
        # 3. If the table has old columns but not new ones, we need to add them
        if 'created' in columns and 'created_at' not in columns:
            print("Adding new timestamp columns...")
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created_at DATETIME")
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated_at DATETIME")
            print("✓ Added new timestamp columns")
            
            # Copy data from old columns to new columns
            print("Copying data from old columns to new columns...")
            cursor.execute("""
                UPDATE events_eventcategory 
                SET created_at = created, updated_at = modified
            """)
            print(f"✓ Copied data ({cursor.rowcount} rows)")
        
        conn.commit()
        conn.close()
        print("✓ SQLite database fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error fixing SQLite database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


if __name__ == '__main__':
    fix_database()
