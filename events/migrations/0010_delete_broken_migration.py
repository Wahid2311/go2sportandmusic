# Migration to delete the broken migration record from django_migrations table

from django.db import migrations


def delete_broken_migration(apps, schema_editor):
    """
    Delete the broken migration record for 0009_fix_null_categories from django_migrations table
    This allows us to re-run migration 0009 with the fixed code
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Delete all broken migration records for 0009
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND name LIKE '0009_%'
            """)
            print(f"✓ Deleted broken migration records (affected: {cursor.rowcount} rows)")
        except Exception as e:
            print(f"⚠ Could not delete broken migration records: {e}")
            # Don't fail the migration, just continue
            pass


def reverse_delete(apps, schema_editor):
    """Reverse migration - not needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_fix_eventcategory_schema'),
    ]

    operations = [
        migrations.RunPython(delete_broken_migration, reverse_delete),
    ]
