#!/usr/bin/env python
"""
Script to fix the broken database state before running migrations.
This script uses raw database connections to safely delete broken migration records.
"""

import os
import sys

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
    """Fix the PostgreSQL database using raw psycopg2"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        print(f"Connecting to PostgreSQL database at {parsed.hostname}:{parsed.port}...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading /
            user=parsed.username,
            password=parsed.password
        )
        cursor = conn.cursor()
        
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'django_migrations'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("✓ django_migrations table doesn't exist yet. Skipping cleanup.")
            conn.close()
            return
        
        # List all current migrations in the database
        print("\nCurrent migrations in database:")
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
        current_migrations = cursor.fetchall()
        for app, name in current_migrations:
            print(f"  - {app}.{name}")
        
        # Delete ALL migrations except 0001_initial and 0002_comprehensive_schema_fix
        print("\n" + "=" * 60)
        print("DELETING ALL BROKEN MIGRATIONS")
        print("=" * 60)
        
        # Delete all migrations except the ones we want to keep
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE NOT (
                (app = 'events' AND name = '0001_initial') OR
                (app = 'events' AND name = '0002_comprehensive_schema_fix') OR
                (app = 'tickets' AND name = '0001_initial') OR
                (app = 'tickets' AND name = '0002_comprehensive_schema_fix')
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"✓ Successfully deleted {deleted_count} broken migration records")
        print("=" * 60)
        
        # Show remaining migrations
        print("\nRemaining migrations in database:")
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
        remaining_migrations = cursor.fetchall()
        if remaining_migrations:
            for app, name in remaining_migrations:
                print(f"  - {app}.{name}")
        else:
            print("  (none - will be created by migrations)")
        
        conn.close()
        print("\n✓ PostgreSQL database fixed successfully!")
        
    except ImportError:
        print("✗ psycopg2 not installed. Skipping PostgreSQL fix.")
    except Exception as e:
        print(f"✗ Error fixing PostgreSQL database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


def fix_sqlite_database(db_path):
    """Fix the SQLite database using raw sqlite3"""
    try:
        import sqlite3
        
        print(f"Connecting to SQLite database at {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_migrations'
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("✓ django_migrations table doesn't exist yet. Skipping cleanup.")
            conn.close()
            return
        
        # List all current migrations in the database
        print("\nCurrent migrations in database:")
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
        current_migrations = cursor.fetchall()
        for app, name in current_migrations:
            print(f"  - {app}.{name}")
        
        # Delete ALL migrations except 0001_initial and 0002_comprehensive_schema_fix
        print("\n" + "=" * 60)
        print("DELETING ALL BROKEN MIGRATIONS")
        print("=" * 60)
        
        # Delete all migrations except the ones we want to keep
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE NOT (
                (app = 'events' AND name = '0001_initial') OR
                (app = 'events' AND name = '0002_comprehensive_schema_fix') OR
                (app = 'tickets' AND name = '0001_initial') OR
                (app = 'tickets' AND name = '0002_comprehensive_schema_fix')
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"✓ Successfully deleted {deleted_count} broken migration records")
        print("=" * 60)
        
        # Show remaining migrations
        print("\nRemaining migrations in database:")
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
        remaining_migrations = cursor.fetchall()
        if remaining_migrations:
            for app, name in remaining_migrations:
                print(f"  - {app}.{name}")
        else:
            print("  (none - will be created by migrations)")
        
        conn.close()
        print("\n✓ SQLite database fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error fixing SQLite database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


if __name__ == '__main__':
    fix_database()
