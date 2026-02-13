# Migration to reset broken migration history and fix schema

from django.db import migrations, connection


def reset_migrations(apps, schema_editor):
    """Completely reset the migration history in the database"""
    with connection.cursor() as cursor:
        # Delete ALL migrations from both apps to start fresh
        cursor.execute("DELETE FROM django_migrations WHERE app IN ('events', 'tickets')")
        
        # Now re-insert only the migrations we want to keep
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) VALUES
            ('events', '0001_initial', NOW()),
            ('events', '0002_event_country_event_sports_type_and_more', NOW()),
            ('events', '0003_category', NOW()),
            ('events', '0004_category_country_category_type_and_more', NOW()),
            ('events', '0005_eventcategory', NOW()),
            ('tickets', '0001_initial', NOW())
        """)
        
        print("✓ Reset migration history successfully")


def reverse_reset(apps, schema_editor):
    """Reverse operation (do nothing)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        migrations.RunPython(reset_migrations, reverse_reset),
    ]
