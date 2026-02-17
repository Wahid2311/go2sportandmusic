from django.db import migrations, models


def fix_schema_and_charges(apps, schema_editor):
    """
    This migration:
    1. Adds missing columns to EventCategory table
    2. Sets correct service charges (20% for normal, 12% for reseller)
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Add missing columns to EventCategory if they don't exist
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass  # Column already exists
        
        # Update Event service charges to correct values
        try:
            cursor.execute("UPDATE events_event SET normal_service_charge = 20")
            cursor.execute("UPDATE events_event SET reseller_service_charge = 12")
        except:
            pass  # Table might not exist yet


def reverse_migration(apps, schema_editor):
    """Reverse function - does nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        migrations.RunPython(fix_schema_and_charges, reverse_migration),
        # Add the missing columns to EventCategory
        migrations.AddField(
            model_name='eventcategory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='eventcategory',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
