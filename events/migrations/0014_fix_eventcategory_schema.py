# Migration to properly fix EventCategory schema and data

from django.db import migrations
from django.utils import timezone


def fix_eventcategory_schema(apps, schema_editor):
    """
    Fix the EventCategory table schema by:
    1. Adding created_at and updated_at columns if they don't exist
    2. Copying data from created/modified if they exist
    3. Inserting Football category with proper timestamps
    """
    with schema_editor.connection.cursor() as cursor:
        current_time = timezone.now().isoformat()
        
        # Check if created_at column exists
        cursor.execute("""
            SELECT name FROM pragma_table_info('events_eventcategory') 
            WHERE name='created_at'
        """)
        has_created_at = cursor.fetchone() is not None
        
        # Check if created column exists
        cursor.execute("""
            SELECT name FROM pragma_table_info('events_eventcategory') 
            WHERE name='created'
        """)
        has_created = cursor.fetchone() is not None
        
        # If created_at doesn't exist but created does, we need to handle the schema
        if not has_created_at and has_created:
            # Add the new columns
            try:
                cursor.execute(f"ALTER TABLE events_eventcategory ADD COLUMN created_at TEXT DEFAULT '{current_time}'")
            except:
                pass
            
            try:
                cursor.execute(f"ALTER TABLE events_eventcategory ADD COLUMN updated_at TEXT DEFAULT '{current_time}'")
            except:
                pass
            
            # Copy data from old columns to new columns
            try:
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET created_at = created, updated_at = modified
                    WHERE created_at IS NULL
                """)
            except:
                pass
        
        # Now insert Football category
        try:
            cursor.execute(f"""
                INSERT OR IGNORE INTO events_eventcategory (name, slug, description, icon, is_active, "order", created, modified, created_at, updated_at)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, '{current_time}', '{current_time}', '{current_time}', '{current_time}')
            """)
        except:
            # If the above fails, try without the old columns
            try:
                cursor.execute(f"""
                    INSERT OR IGNORE INTO events_eventcategory (name, slug, description, icon, is_active, "order", created_at, updated_at)
                    VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, '{current_time}', '{current_time}')
                """)
            except:
                pass
        
        # Get the Football category ID and update NULL categories
        cursor.execute("SELECT id FROM events_eventcategory WHERE slug = 'football' LIMIT 1")
        result = cursor.fetchone()
        if result:
            football_id = result[0]
            try:
                cursor.execute(f"UPDATE events_event SET category_id = {football_id} WHERE category_id IS NULL")
            except:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_add_timestamps_to_eventcategory'),
    ]

    operations = [
        migrations.RunPython(fix_eventcategory_schema, migrations.RunPython.noop),
    ]
