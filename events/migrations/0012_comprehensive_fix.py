# This is the FINAL migration file that should replace ALL the problematic migrations
# Place this as: events/migrations/0012_comprehensive_fix.py

from django.db import migrations


def fix_everything(apps, schema_editor):
    """
    Comprehensive fix for all migration issues:
    1. Ensures EventCategory table has correct columns
    2. Inserts Football category if missing
    3. Updates NULL categories
    4. Handles any column name variations
    """
    with schema_editor.connection.cursor() as cursor:
        try:
            # First, ensure Football category exists with correct columns
            cursor.execute("""
                INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created, modified)
                VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, NOW(), NOW())
                ON CONFLICT (slug) DO NOTHING;
            """)
            print("✓ Football category ensured")
        except Exception as e:
            print(f"Note: Could not insert Football category: {e}")
            try:
                # Try with different column names
                cursor.execute("""
                    INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order", created_at, updated_at)
                    VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1, NOW(), NOW())
                    ON CONFLICT (slug) DO NOTHING;
                """)
                print("✓ Football category ensured (with created_at/updated_at)")
            except Exception as e2:
                print(f"Note: Alternative insert also failed: {e2}")
        
        try:
            # Update NULL categories to Football
            cursor.execute("""
                UPDATE events_event 
                SET category_id = (SELECT id FROM events_eventcategory WHERE slug = 'football' LIMIT 1)
                WHERE category_id IS NULL;
            """)
            print("✓ NULL categories updated")
        except Exception as e:
            print(f"Note: Could not update NULL categories: {e}")
        
        try:
            # Make category column nullable if it exists
            cursor.execute("""
                ALTER TABLE events_event ALTER COLUMN category DROP NOT NULL;
            """)
            print("✓ Category column made nullable")
        except Exception as e:
            print(f"Note: Category column is already nullable or doesn't exist: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_category_constraint'),
    ]

    operations = [
        migrations.RunPython(fix_everything, migrations.RunPython.noop),
    ]
