#!/usr/bin/env python
"""
Script to fix the broken database state before running migrations.
This script uses raw database connections to safely delete broken migration records,
and also ensures that tables missing from the base migrations are created.

Tables ensured by this script (not in 0001_initial or 0002_comprehensive_schema_fix):
  - tickets_ticketreservation  (added in 0012, needed for event/ticket cascade delete)
  - tickets_ticketpdf          (added in 0012, needed for PDF upload feature)
"""

import os
import sys


# ─── SQL to create missing tables ────────────────────────────────────────────

# PostgreSQL version
POSTGRES_CREATE_MISSING_TABLES = [
    # tickets_ticketpdf
    """
    CREATE TABLE IF NOT EXISTS tickets_ticketpdf (
        id          BIGSERIAL PRIMARY KEY,
        file        VARCHAR(100) NOT NULL,
        is_sold     BOOLEAN NOT NULL DEFAULT FALSE,
        uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ticket_id   INTEGER NOT NULL REFERENCES tickets_ticket(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS tickets_ticketpdf_ticket_id_idx
        ON tickets_ticketpdf (ticket_id)
    """,
    # tickets_ticketreservation
    """
    CREATE TABLE IF NOT EXISTS tickets_ticketreservation (
        id                  SERIAL PRIMARY KEY,
        quantity_reserved   INTEGER NOT NULL CHECK (quantity_reserved >= 0),
        created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        expires_at          TIMESTAMPTZ NOT NULL,
        is_expired          BOOLEAN NOT NULL DEFAULT FALSE,
        buyer_id            UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
        order_id            UUID UNIQUE REFERENCES tickets_order(id) ON DELETE CASCADE,
        ticket_id           INTEGER NOT NULL REFERENCES tickets_ticket(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS tickets_tic_ticket__800a4a_idx
        ON tickets_ticketreservation (ticket_id, is_expired)
    """,
    """
    CREATE INDEX IF NOT EXISTS tickets_tic_expires_5be74a_idx
        ON tickets_ticketreservation (expires_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS tickets_tic_order_i_70e16b_idx
        ON tickets_ticketreservation (order_id)
    """,
]

# SQLite version (executescript format - semicolon separated)
SQLITE_CREATE_MISSING_TABLES = """
CREATE TABLE IF NOT EXISTS tickets_ticketpdf (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file        VARCHAR(100) NOT NULL,
    is_sold     BOOLEAN NOT NULL DEFAULT 0,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ticket_id   INTEGER NOT NULL REFERENCES tickets_ticket(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS tickets_ticketpdf_ticket_id_idx
    ON tickets_ticketpdf (ticket_id);
CREATE TABLE IF NOT EXISTS tickets_ticketreservation (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity_reserved   INTEGER NOT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          DATETIME NOT NULL,
    is_expired          BOOLEAN NOT NULL DEFAULT 0,
    buyer_id            CHAR(32) NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    order_id            INTEGER UNIQUE REFERENCES tickets_order(id) ON DELETE CASCADE,
    ticket_id           INTEGER NOT NULL REFERENCES tickets_ticket(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS tickets_tic_ticket__800a4a_idx
    ON tickets_ticketreservation (ticket_id, is_expired);
CREATE INDEX IF NOT EXISTS tickets_tic_expires_5be74a_idx
    ON tickets_ticketreservation (expires_at);
CREATE INDEX IF NOT EXISTS tickets_tic_order_i_70e16b_idx
    ON tickets_ticketreservation (order_id);
"""


# ─── PostgreSQL ───────────────────────────────────────────────────────────────

def fix_postgres_database(database_url):
    """Fix the PostgreSQL database using raw psycopg2"""
    try:
        import psycopg2
        from urllib.parse import urlparse

        parsed = urlparse(database_url)

        print(f"Connecting to PostgreSQL database at {parsed.hostname}:{parsed.port}...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        cursor = conn.cursor()

        # ── 1. Clean up broken migration records ──────────────────────────
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'django_migrations'
            )
        """)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            print("✓ django_migrations table doesn't exist yet. Skipping cleanup.")
        else:
            print("\nCurrent migrations in database:")
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            current_migrations = cursor.fetchall()
            for app, name in current_migrations:
                print(f"  - {app}.{name}")

            print("\n" + "=" * 60)
            print("DELETING ALL BROKEN MIGRATIONS")
            print("=" * 60)

            cursor.execute("""
                DELETE FROM django_migrations
                WHERE NOT (
                    (app = 'events'  AND name = '0001_initial') OR
                    (app = 'events'  AND name = '0002_comprehensive_schema_fix') OR
                    (app = 'tickets' AND name = '0001_initial') OR
                    (app = 'tickets' AND name = '0002_comprehensive_schema_fix')
                )
            """)
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"✓ Successfully deleted {deleted_count} broken migration records")

            print("\nRemaining migrations in database:")
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            remaining = cursor.fetchall()
            if remaining:
                for app, name in remaining:
                    print(f"  - {app}.{name}")
            else:
                print("  (none - will be created by migrations)")

        # ── 2. Create missing tables ───────────────────────────────────────
        print("\n" + "=" * 60)
        print("ENSURING MISSING TABLES EXIST")
        print("=" * 60)
        try:
            for stmt in POSTGRES_CREATE_MISSING_TABLES:
                cursor.execute(stmt)
            conn.commit()
            print("✓ tickets_ticketpdf table ensured")
            print("✓ tickets_ticketreservation table ensured")
        except Exception as e:
            conn.rollback()
            print(f"✗ Error creating missing tables: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail — continue so migrations can still run

        conn.close()
        print("\n✓ PostgreSQL database fixed successfully!")

    except ImportError:
        print("✗ psycopg2 not installed. Skipping PostgreSQL fix.")
    except Exception as e:
        print(f"✗ Error fixing PostgreSQL database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


# ─── SQLite ───────────────────────────────────────────────────────────────────

def fix_sqlite_database(db_path):
    """Fix the SQLite database using raw sqlite3"""
    try:
        import sqlite3

        print(f"Connecting to SQLite database at {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ── 1. Clean up broken migration records ──────────────────────────
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='django_migrations'
        """)
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            print("✓ django_migrations table doesn't exist yet. Skipping cleanup.")
        else:
            print("\nCurrent migrations in database:")
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            current_migrations = cursor.fetchall()
            for app, name in current_migrations:
                print(f"  - {app}.{name}")

            print("\n" + "=" * 60)
            print("DELETING ALL BROKEN MIGRATIONS")
            print("=" * 60)

            cursor.execute("""
                DELETE FROM django_migrations
                WHERE NOT (
                    (app = 'events'  AND name = '0001_initial') OR
                    (app = 'events'  AND name = '0002_comprehensive_schema_fix') OR
                    (app = 'tickets' AND name = '0001_initial') OR
                    (app = 'tickets' AND name = '0002_comprehensive_schema_fix')
                )
            """)
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"✓ Successfully deleted {deleted_count} broken migration records")

            print("\nRemaining migrations in database:")
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            remaining = cursor.fetchall()
            if remaining:
                for app, name in remaining:
                    print(f"  - {app}.{name}")
            else:
                print("  (none - will be created by migrations)")

        # ── 2. Create missing tables ───────────────────────────────────────
        print("\n" + "=" * 60)
        print("ENSURING MISSING TABLES EXIST")
        print("=" * 60)
        try:
            conn.executescript(SQLITE_CREATE_MISSING_TABLES)
            conn.commit()
            print("✓ tickets_ticketpdf table ensured")
            print("✓ tickets_ticketreservation table ensured")
        except Exception as e:
            print(f"✗ Error creating missing tables: {e}")
            import traceback
            traceback.print_exc()

        conn.close()
        print("\n✓ SQLite database fixed successfully!")

    except Exception as e:
        print(f"✗ Error fixing SQLite database: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue


# ─── Entry point ─────────────────────────────────────────────────────────────

def fix_database():
    """Fix the broken database state"""
    database_url = os.environ.get('DATABASE_URL')
    db_path = '/app/db.sqlite3'

    if database_url and database_url.startswith('postgres'):
        print("Using PostgreSQL database...")
        fix_postgres_database(database_url)
    elif os.path.exists(db_path):
        print(f"Using SQLite database at {db_path}...")
        fix_sqlite_database(db_path)
    else:
        print("No database found. Will be created by migrations.")
        return


if __name__ == '__main__':
    fix_database()
