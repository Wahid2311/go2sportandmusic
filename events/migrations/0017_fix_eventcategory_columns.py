# Migration to fix EventCategory columns - handles both old and new versions of 0009

from django.db import migrations


def fix_eventcategory_data(apps, schema_editor):
    """Fix EventCategory table if needed"""
    with schema_editor.connection.cursor() as cursor:
        try:
            # Try to insert Football category with correct columns
            cursor.execute("""
                INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created, modified)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, NOW(), NOW())
                ON CONFLICT (slug) DO NOTHING;
            """)
        except Exception as e:
            # If that fails, try with created_at/updated_at
            try:
                cursor.execute("""
                    INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created_at, updated_at)
                    VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, NOW(), NOW())
                    ON CONFLICT (slug) DO NOTHING;
                """)
            except Exception as e2:
                print(f"Could not insert Football category: {e2}")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(fix_eventcategory_data, migrations.RunPython.noop),
    ]
