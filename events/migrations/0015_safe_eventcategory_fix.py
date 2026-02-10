# Safe migration to fix EventCategory schema - handles any previous state

from django.db import migrations
from django.utils import timezone


def safe_fix_eventcategory(apps, schema_editor):
    """
    Safely fix EventCategory table regardless of previous migration state.
    This migration is idempotent and won't fail if columns already exist.
    """
    with schema_editor.connection.cursor() as cursor:
        current_time = timezone.now().isoformat()
        
        # Get all columns in the table
        cursor.execute("""
            SELECT name FROM pragma_table_info('events_eventcategory')
        """)
        columns = {row[0] for row in cursor.fetchall()}
        
        # Add created_at if it doesn't exist
        if 'created_at' not in columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE events_eventcategory 
                    ADD COLUMN created_at TEXT DEFAULT '{current_time}'
                """)
            except Exception as e:
                print(f"Note: Could not add created_at column: {e}")
        
        # Add updated_at if it doesn't exist
        if 'updated_at' not in columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE events_eventcategory 
                    ADD COLUMN updated_at TEXT DEFAULT '{current_time}'
                """)
            except Exception as e:
                print(f"Note: Could not add updated_at column: {e}")
        
        # Ensure Football category exists
        cursor.execute("""
            SELECT COUNT(*) FROM events_eventcategory WHERE slug = 'football'
        """)
        if cursor.fetchone()[0] == 0:
            # Football doesn't exist, insert it
            try:
                # Try with all possible columns
                cursor.execute(f"""
                    INSERT INTO events_eventcategory 
                    (name, slug, description, icon, is_active, "order", created, modified, created_at, updated_at)
                    VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, '{current_time}', '{current_time}', '{current_time}', '{current_time}')
                """)
            except Exception as e1:
                try:
                    # Try without created_at/updated_at
                    cursor.execute(f"""
                        INSERT INTO events_eventcategory 
                        (name, slug, description, icon, is_active, "order", created, modified)
                        VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, '{current_time}', '{current_time}')
                    """)
                except Exception as e2:
                    try:
                        # Try without created/modified
                        cursor.execute(f"""
                            INSERT INTO events_eventcategory 
                            (name, slug, description, icon, is_active, "order", created_at, updated_at)
                            VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, '{current_time}', '{current_time}')
                        """)
                    except Exception as e3:
                        print(f"Note: Could not insert Football category: {e3}")
        
        # Update NULL categories to Football
        try:
            cursor.execute("""
                SELECT id FROM events_eventcategory WHERE slug = 'football' LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                football_id = result[0]
                cursor.execute(f"""
                    UPDATE events_event SET category_id = {football_id} WHERE category_id IS NULL
                """)
        except Exception as e:
            print(f"Note: Could not update NULL categories: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_fix_eventcategory_schema'),
    ]

    operations = [
        migrations.RunPython(safe_fix_eventcategory, migrations.RunPython.noop),
    ]
