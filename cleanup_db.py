#!/usr/bin/env python
"""
Script to clean up broken migrations from the database
This script is called from the Procfile before running migrations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
sys.path.insert(0, os.path.dirname(__file__))

try:
    django.setup()
    from django.db import connection
    from django.apps import apps
    
    # Make sure the django_migrations table exists
    with connection.cursor() as cursor:
        # Create the table if it doesn't exist (for first run)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied DATETIME NOT NULL
            )
        """)
        
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
        
        # Commit the transaction
        connection.commit()
        
except Exception as e:
    print(f"Error cleaning up migrations: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✓ Database cleanup completed successfully!")
