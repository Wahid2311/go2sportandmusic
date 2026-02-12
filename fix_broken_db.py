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
        
        # 1. Delete ALL problematic migration records from both apps
        print("Deleting broken migration records from events app...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name = '0006_add_eventcategory_timestamps' OR
                name = '0006_placeholder' OR
                name = '0007_set_default_category' OR
                name = '0009_fix_eventcategory_schema' OR
                name = '0009_fix_null_categories' OR
                name = '0009_verify_schema' OR
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
        events_deleted = cursor.rowcount
        print(f"✓ Deleted {events_deleted} broken migration records from events app")
        
        print("Deleting broken migration records from tickets app...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'tickets' AND (
                name = '0002_alter_ticket_upload_file' OR
                name = '0003_ticket_bundle_id_ticket_sell_together' OR
                name = '0004_stripe_fields' OR
                name = '0005_alter_ticket_upload_file' OR
                name LIKE '0006_%' OR 
                name LIKE '0007_%' OR 
                name LIKE '0008_%' OR 
                name LIKE '0009_%' OR 
                name LIKE '0010_%'
            )
        """)
        tickets_deleted = cursor.rowcount
        print(f"✓ Deleted {tickets_deleted} broken migration records from tickets app")
        
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
        
        # 1. Delete ALL problematic migration records from both apps
        print("Deleting broken migration records from events app...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name = '0006_add_eventcategory_timestamps' OR
                name = '0006_placeholder' OR
                name = '0007_set_default_category' OR
                name = '0009_fix_eventcategory_schema' OR
                name = '0009_fix_null_categories' OR
                name = '0009_verify_schema' OR
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
        events_deleted = cursor.rowcount
        print(f"✓ Deleted {events_deleted} broken migration records from events app")
        
        print("Deleting broken migration records from tickets app...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'tickets' AND (
                name = '0002_alter_ticket_upload_file' OR
                name = '0003_ticket_bundle_id_ticket_sell_together' OR
                name = '0004_stripe_fields' OR
                name = '0005_alter_ticket_upload_file' OR
                name LIKE '0006_%' OR 
                name LIKE '0007_%' OR 
                name LIKE '0008_%' OR 
                name LIKE '0009_%' OR 
                name LIKE '0010_%'
            )
        """)
        tickets_deleted = cursor.rowcount
        print(f"✓ Deleted {tickets_deleted} broken migration records from tickets app")
        
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
