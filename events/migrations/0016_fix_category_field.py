# SQL migration to fix category field - handles all edge cases

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_merge'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward: Make category nullable if it exists
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='events_event' AND column_name='category'
                ) THEN
                    ALTER TABLE events_event ALTER COLUMN category DROP NOT NULL;
                END IF;
            END $$;
            """,
            # Reverse: No need to do anything on reverse
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
