# Migration to reset broken migration state and fix EventCategory data

from django.db import migrations
from django.utils import timezone


def reset_and_fix(apps, schema_editor):
    """
    This migration handles the case where previous migrations failed but were recorded as applied.
    It will:
    1. Remove the failed migration records from django_migrations
    2. Ensure Football category exists
    3. Update NULL categories
    """
    with schema_editor.connection.cursor() as cursor:
        current_time = timezone.now().isoformat()
        
        # First, remove failed migration records so they can be retried
        # This is safe because we're about to fix the data anyway
        try:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND name IN (
                    '0010_allow_null_category',
                    '0011_remove_category_constraint',
                    '0012_fix_database_schema',
                    '0013_add_timestamps_to_eventcategory',
                    '0014_fix_eventcategory_schema'
                )
            """)
        except Exception as e:
            print(f"Note: Could not clean migration history: {e}")
        
        # Now ensure Football category exists with all required fields
        cursor.execute("""
            SELECT COUNT(*) FROM events_eventcategory WHERE slug = 'football'
        """)
        football_exists = cursor.fetchone()[0] > 0
        
        if not football_exists:
            # Get the columns that exist in the table
            cursor.execute("""
                SELECT name FROM pragma_table_info('events_eventcategory')
            """)
            columns = {row[0] for row in cursor.fetchall()}
            
            # Build the INSERT statement based on what columns exist
            fields = ['name', 'slug', 'description', 'icon', 'is_active', '"order"']
            values = ["'Football'", "'football'", "'Football events'", "'bi-soccer'", "1", "1"]
            
            if 'created' in columns:
                fields.append('created')
                values.append(f"'{current_time}'")
            
            if 'modified' in columns:
                fields.append('modified')
                values.append(f"'{current_time}'")
            
            if 'created_at' in columns:
                fields.append('created_at')
                values.append(f"'{current_time}'")
            
            if 'updated_at' in columns:
                fields.append('updated_at')
                values.append(f"'{current_time}'")
            
            insert_sql = f"""
                INSERT OR IGNORE INTO events_eventcategory ({', '.join(fields)})
                VALUES ({', '.join(values)})
            """
            
            try:
                cursor.execute(insert_sql)
            except Exception as e:
                print(f"Note: Could not insert Football category: {e}")
        
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
        ('events', '0015_safe_eventcategory_fix'),
    ]

    operations = [
        migrations.RunPython(reset_and_fix, migrations.RunPython.noop),
    ]
