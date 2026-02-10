# Migration to fake 0009 and fix the EventCategory issue

from django.db import migrations


def fake_and_fix_0009(apps, schema_editor):
    """
    This function will:
    1. Delete the failed 0009 migration from django_migrations
    2. Insert Football category with correct columns
    3. Update NULL categories
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Delete the failed 0009 migration so it can be re-run or skipped
            cursor.execute(
                "DELETE FROM django_migrations WHERE app='events' AND name='0009_fix_null_categories'"
            )
        except Exception as e:
            print(f"Could not delete 0009: {e}")
        
        try:
            # Now insert Football category with CORRECT columns
            cursor.execute("""
                INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created, modified)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, NOW(), NOW())
                ON CONFLICT (slug) DO NOTHING;
            """)
            
            # Get the Football category ID
            cursor.execute("SELECT id FROM events_eventcategory WHERE slug = 'football' LIMIT 1;")
            result = cursor.fetchone()
            if result:
                football_id = result[0]
                # Update all NULL categories to Football
                try:
                    cursor.execute(f"UPDATE events_event SET category_id = {football_id} WHERE category_id IS NULL;")
                except Exception as e:
                    print(f"Could not update categories: {e}")
        except Exception as e:
            print(f"Could not insert Football category: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_fix_0009_issue'),
    ]

    operations = [
        migrations.RunPython(fake_and_fix_0009, migrations.RunPython.noop),
    ]
