# Migration to fix the 0009 column name issue

from django.db import migrations


def fix_0009_columns(apps, schema_editor):
    """
    Fix the issue where 0009 tries to insert with created_at/updated_at
    but the table only has created/modified columns
    """
    with schema_editor.connection.cursor() as cursor:
        try:
            # Try to insert Football category with correct columns
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
        ('events', '0020_merge_all_conflicts'),
    ]

    operations = [
        migrations.RunPython(fix_0009_columns, migrations.RunPython.noop),
    ]
