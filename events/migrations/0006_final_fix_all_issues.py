from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def reset_migration_history_and_fix_schema(apps, schema_editor):
    """
    This migration:
    1. Deletes only the broken migration records from the database
    2. Adds missing columns to EventCategory table
    3. Sets correct service charges (20% for normal, 12% for reseller)
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Delete ONLY the broken migration records that are causing issues
        broken_migrations = [
            ('events', '0006_add_eventcategory_timestamps'),
            ('events', '0006_placeholder'),
            ('events', '0007_set_default_category'),
            ('events', '0008_fix_service_charges_and_reseller_purchase'),
            ('events', '0009_fix_eventcategory_schema'),
            ('events', '0009_fix_null_categories'),
            ('events', '0009_verify_schema'),
            ('events', '0006_final_fix_all_issues'),
            ('tickets', '0002_alter_ticket_upload_file'),
            ('tickets', '0002_alter_ticket_seats'),
            ('tickets', '0003_ticket_bundle_id_ticket_sell_together'),
            ('tickets', '0004_stripe_fields'),
            ('tickets', '0005_alter_ticket_upload_file'),
            ('tickets', '0006_recalculate_ticket_prices'),
        ]
        
        for app, name in broken_migrations:
            try:
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app = %s AND name = %s",
                    (app, name)
                )
            except:
                pass  # Migration record doesn't exist, that's fine
        
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
            cursor.execute("UPDATE events_event SET normal_service_charge = 20 WHERE normal_service_charge != 20")
            cursor.execute("UPDATE events_event SET reseller_service_charge = 12 WHERE reseller_service_charge != 12")
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
        migrations.RunPython(reset_migration_history_and_fix_schema, reverse_migration),
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
