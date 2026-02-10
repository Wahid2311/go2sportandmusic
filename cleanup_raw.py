#!/usr/bin/env python
"""
Raw database cleanup script that doesn't use Django
This runs before Django migrations to clean up broken migration records
"""
import os
import sqlite3
import sys

def cleanup_database():
    """Clean up broken migrations using raw SQLite"""
    
    # Get the database path from environment or use default
    db_path = os.environ.get('DATABASE_URL', '')
    
    # Parse DATABASE_URL if it's a sqlite URL
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    elif not db_path or not db_path.endswith('.sqlite3'):
        # Default to db.sqlite3 in the current directory
        db_path = 'db.sqlite3'
    
    print(f"Attempting to clean up database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"⚠ Database file not found: {db_path}")
        print("This is normal for the first deployment - database will be created by migrations")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_migrations'
        """)
        
        if not cursor.fetchone():
            print("⚠ django_migrations table doesn't exist yet - skipping cleanup")
            conn.close()
            return True
        
        # Delete all broken migrations from events app (0009 and above)
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
        
        deleted = cursor.rowcount
        print(f"✓ Deleted {deleted} broken migration records")
        
        conn.commit()
        conn.close()
        
        print("✓ Database cleanup completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error cleaning up database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = cleanup_database()
    sys.exit(0 if success else 1)
