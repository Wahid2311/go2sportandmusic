# Migration to clean up broken migrations from the database

from django.db import migrations


def cleanup_broken_migrations(apps, schema_editor):
    """Delete broken migrations from django_migrations table"""
    from django.db import connection
    cursor = connection.cursor()
    
    # Delete the problematic migrations that are causing issues
    broken_migrations = [
        '0013_alter_category_nullable',
        '0013_merge', 
        '0014_merge',
    ]
    
    for migration_name in broken_migrations:
        try:
            cursor.execute(
                "DELETE FROM django_migrations WHERE app='events' AND name=%s",
                [migration_name]
            )
        except Exception as e:
            print(f"Could not delete migration {migration_name}: {e}")


def reverse_cleanup(apps, schema_editor):
    """Nothing to do on reverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_category_constraint'),
    ]

    operations = [
        migrations.RunPython(cleanup_broken_migrations, reverse_cleanup),
    ]
