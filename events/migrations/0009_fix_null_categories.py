# Migration to fix NULL category values using raw SQL

from django.db import migrations
from django.utils import timezone


def fix_null_categories(apps, schema_editor):
    """Set all NULL categories using raw SQL to avoid ORM column mismatch"""
    # Use raw SQL to ensure Football category exists
    with schema_editor.connection.cursor() as cursor:
        # First, ensure Football category exists
        now = timezone.now().isoformat()
        cursor.execute("""
            INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created_at, updated_at)
            VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, ?, ?)
            ON CONFLICT (slug) DO NOTHING;
        """, [now, now])
        
        # Get the Football category ID
        cursor.execute("SELECT id FROM events_eventcategory WHERE slug = 'football' LIMIT 1;")
        result = cursor.fetchone()
        if result:
            football_id = result[0]
            # Update all NULL categories to Football
            cursor.execute(f"UPDATE events_event SET category_id = {football_id} WHERE category_id IS NULL;")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(fix_null_categories, migrations.RunPython.noop),
    ]
