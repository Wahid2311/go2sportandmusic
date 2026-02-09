# This migration depends on the ORIGINAL 0009 version that Railway has
# It will fix the column names issue

from django.db import migrations


def add_missing_columns(apps, schema_editor):
    """Add created and modified columns if they don't exist"""
    with schema_editor.connection.cursor() as cursor:
        try:
            # Check if columns exist and add them if needed
            cursor.execute("""
                ALTER TABLE events_eventcategory 
                ADD COLUMN IF NOT EXISTS created TIMESTAMP DEFAULT NOW(),
                ADD COLUMN IF NOT EXISTS modified TIMESTAMP DEFAULT NOW();
            """)
        except Exception as e:
            print(f"Note: {str(e)}")


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0008, not 0009, to avoid the conflict
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, migrations.RunPython.noop),
    ]
