# Generated migration to fix database schema issues with raw SQL

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_category_constraint'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward migration - fix the database
            """
            -- Ensure Football category exists
            INSERT INTO events_eventcategory (name, slug, description, icon, is_active, "order")
            VALUES ('Football', 'football', 'Football events', 'bi-soccer', true, 1)
            ON CONFLICT (slug) DO NOTHING;
            
            -- Update all NULL categories to Football
            UPDATE events_event SET category_legacy = 'Football' WHERE category_legacy IS NULL;
            
            -- Make category column nullable
            ALTER TABLE events_event ALTER COLUMN category DROP NOT NULL;
            """,
            # Reverse migration
            """
            -- Reverse: restore category NOT NULL constraint
            ALTER TABLE events_event ALTER COLUMN category SET NOT NULL;
            """,
            state_operations=[]
        ),
    ]
