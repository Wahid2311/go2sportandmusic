#!/usr/bin/env python
"""
Direct database fix script - runs before migrations to clean up broken migration state
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.db import connection

def fix_database():
    """Fix the database by cleaning up broken migrations and ensuring data exists"""
    with connection.cursor() as cursor:
        print("Starting database fix...")
        
        # 1. Delete broken migration records
        try:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND name LIKE '0009_%'
            """)
            print(f"✓ Deleted broken migration records (affected: {cursor.rowcount} rows)")
        except Exception as e:
            print(f"⚠ Could not delete migration records: {e}")
        
        # 2. Ensure Football category exists
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO events_eventcategory 
                (name, slug, description, icon, is_active, "order", created, modified)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, datetime('now'), datetime('now'))
            """)
            print(f"✓ Ensured Football category exists (affected: {cursor.rowcount} rows)")
        except Exception as e:
            print(f"⚠ Could not insert Football category: {e}")
        
        # 3. Update any NULL categories to Football
        try:
            cursor.execute("""
                UPDATE events_eventcategory 
                SET category_id = (SELECT id FROM events_eventcategory WHERE slug = 'football')
                WHERE category_id IS NULL AND slug != 'football'
            """)
            print(f"✓ Updated NULL categories to Football (affected: {cursor.rowcount} rows)")
        except Exception as e:
            print(f"⚠ Could not update NULL categories: {e}")
        
        print("Database fix completed!")

if __name__ == '__main__':
    try:
        fix_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
