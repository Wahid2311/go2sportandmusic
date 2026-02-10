# Migration to mark failed migrations as unapplied so they can be retried

from django.db import migrations


def mark_unapplied(apps, schema_editor):
    """
    Mark migration 0009 as unapplied so it can be retried with the new code.
    """
    try:
        with schema_editor.connection.cursor() as cursor:
            # Delete the failed migration record so it can be retried
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'events' AND name = '0009_fix_null_categories'
            """)
    except Exception as e:
        # Silently ignore any errors
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(mark_unapplied, migrations.RunPython.noop),
    ]
