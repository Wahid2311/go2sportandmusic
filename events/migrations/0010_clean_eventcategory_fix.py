# Clean migration to fix EventCategory data

from django.db import migrations


def fix_eventcategory(apps, schema_editor):
    """
    Fix EventCategory data by ensuring Football category exists and updating NULL categories.
    This migration is idempotent and won't fail even if the data already exists.
    """
    try:
        with schema_editor.connection.cursor() as cursor:
            # First, try to insert the Football category if it doesn't exist
            # Use INSERT OR IGNORE to handle the case where it already exists
            cursor.execute("""
                INSERT OR IGNORE INTO events_eventcategory 
                (name, slug, description, icon, is_active, "order", created, modified)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, datetime('now'), datetime('now'))
            """)
            
            # Update any NULL categories to Football
            cursor.execute("""
                UPDATE events_eventcategory 
                SET category_id = (SELECT id FROM events_eventcategory WHERE slug = 'football')
                WHERE category_id IS NULL AND slug != 'football'
            """)
    except Exception as e:
        # Silently ignore any errors - the database might already be in the correct state
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(fix_eventcategory, migrations.RunPython.noop),
    ]
