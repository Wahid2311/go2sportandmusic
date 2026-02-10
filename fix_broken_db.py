#!/usr/bin/env python
"""
Script to fix the broken database state before running migrations.
This script directly uses sqlite3 to:
1. Delete broken migration records
2. Fix the EventCategory schema
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = '/app/db.sqlite3'

def fix_database():
    """Fix the broken database state"""
    
    # Check if the database file exists
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} does not exist yet. Will be created by migrations.")
        return
    
    print(f"Fixing database at {DB_PATH}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Delete all broken migration records for 0009 and later
        print("Deleting broken migration records...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name LIKE '0009_%' OR 
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
        print("✓ Database fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error fixing database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue
        pass


if __name__ == '__main__':
    fix_database()
