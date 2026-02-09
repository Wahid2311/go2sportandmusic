# Migration to remove NOT NULL constraint from category column

from django.db import migrations


def remove_not_null_constraint(apps, schema_editor):
    """Remove NOT NULL constraint from category column using raw SQL"""
    with schema_editor.connection.cursor() as cursor:
        try:
            # For PostgreSQL
            cursor.execute("""
                ALTER TABLE events_event 
                ALTER COLUMN category_id DROP NOT NULL;
            """)
        except Exception as e:
            print(f"Note: {str(e)}")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_allow_null_category'),
    ]

    operations = [
        migrations.RunPython(remove_not_null_constraint, migrations.RunPython.noop),
    ]
