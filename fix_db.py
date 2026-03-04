#!/usr/bin/env python
"""
Direct database fix script - runs before migrations to clean up broken migration state
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.db import connection

def fix_database():
    """Fix the database by cleaning up broken migrations and ensuring data exists"""
    with connection.cursor() as cursor:
        print("Starting database fix...")
        
        # 1. Delete ALL old migration 0009 records (including the broken fix_null_categories one)
        try:
            # Delete all 0009 migrations to allow the new one to run
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND name LIKE '0009_%'
            """)
            deleted_count = cursor.rowcount
            print(f"✓ Deleted broken migration records (affected: {deleted_count} rows)")
            
            # Also delete any 0010+ migrations that might have been partially applied
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND (name LIKE '0010_%' OR name LIKE '0011_%' OR name LIKE '0012_%' OR name LIKE '0013_%' OR name LIKE '0014_%' OR name LIKE '0015_%' OR name LIKE '0016_%' OR name LIKE '0017_%' OR name LIKE '0018_%' OR name LIKE '0019_%')
            """)
            print(f"✓ Deleted other broken migration records (affected: {cursor.rowcount} rows)")
        except Exception as e:
            print(f"⚠ Could not delete migration records: {e}")
        
        # 2. Check if EventCategory table has the old schema (created/modified) or new schema (created_at/updated_at)
        try:
            # Get column names from EventCategory table
            cursor.execute("PRAGMA table_info(events_eventcategory)")
            columns = {row[1] for row in cursor.fetchall()}
            
            if 'created' in columns and 'modified' in columns and 'created_at' not in columns:
                print("⚠ EventCategory has old schema (created/modified) - migrations will fix this")
            elif 'created_at' in columns and 'updated_at' in columns:
                print("✓ EventCategory has new schema (created_at/updated_at)")
            else:
                print(f"⚠ EventCategory schema is unclear. Columns: {columns}")
        except Exception as e:
            print(f"⚠ Could not check EventCategory schema: {e}")
        
        # 3. Try to insert Football category with the correct field names
        try:
            now = datetime.now().isoformat()
            # Try with new field names first
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO events_eventcategory 
                    (name, slug, description, icon, is_active, "order", created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, ['Football', 'football', 'Football events', 'bi-soccer', 1, 1, now, now])
                print(f"✓ Ensured Football category exists with new schema (affected: {cursor.rowcount} rows)")
            except Exception as e1:
                # If that fails, try with old field names
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO events_eventcategory 
                        (name, slug, description, icon, is_active, "order", created, modified)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, ['Football', 'football', 'Football events', 'bi-soccer', 1, 1, now, now])
                    print(f"✓ Ensured Football category exists with old schema (affected: {cursor.rowcount} rows)")
                except Exception as e2:
                    print(f"⚠ Could not insert Football category with either schema: {e1}, {e2}")
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
