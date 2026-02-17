from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def reset_migration_history_and_fix_schema(apps, schema_editor):
    """
    This migration:
    1. Clears all broken migration records from the database
    2. Re-inserts only valid migrations
    3. Adds missing columns to EventCategory table
    4. Sets correct service charges (20% for normal, 12% for reseller)
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Get the database engine type
        db_engine = connection.settings_dict['ENGINE']
        is_postgres = 'postgresql' in db_engine
        is_sqlite = 'sqlite' in db_engine
        
        # Delete all migration records to start fresh
        cursor.execute("DELETE FROM django_migrations WHERE app IN ('events', 'tickets')")
        
        # Re-insert only the valid migrations
        if is_postgres:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) VALUES
                ('events', '0001_initial', NOW()),
                ('events', '0002_event_country_event_sports_type_and_more', NOW()),
                ('events', '0003_category', NOW()),
                ('events', '0004_category_country_category_type_and_more', NOW()),
                ('events', '0005_eventcategory', NOW()),
                ('tickets', '0001_initial', NOW()),
                ('tickets', '0002_alter_ticket_seats', NOW()),
                ('tickets', '0003_ticket_bundle_id_ticket_sell_together', NOW()),
                ('tickets', '0004_alter_ticket_sell_price_for_normal_and_more', NOW()),
                ('tickets', '0005_alter_ticket_upload_file', NOW())
            """)
        elif is_sqlite:
            from datetime import datetime
            now = datetime.now().isoformat()
            cursor.execute(f"""
                INSERT INTO django_migrations (app, name, applied) VALUES
                ('events', '0001_initial', '{now}'),
                ('events', '0002_event_country_event_sports_type_and_more', '{now}'),
                ('events', '0003_category', '{now}'),
                ('events', '0004_category_country_category_type_and_more', '{now}'),
                ('events', '0005_eventcategory', '{now}'),
                ('tickets', '0001_initial', '{now}'),
                ('tickets', '0002_alter_ticket_seats', '{now}'),
                ('tickets', '0003_ticket_bundle_id_ticket_sell_together', '{now}'),
                ('tickets', '0004_alter_ticket_sell_price_for_normal_and_more', '{now}'),
                ('tickets', '0005_alter_ticket_upload_file', '{now}')
            """)
        
        # Add missing columns to EventCategory if they don't exist
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass  # Column already exists


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
        # Update Event model to set correct service charges
        migrations.AlterField(
            model_name='event',
            name='normal_service_charge',
            field=models.DecimalField(decimal_places=2, default=20, max_digits=5),
        ),
        migrations.AlterField(
            model_name='event',
            name='reseller_service_charge',
            field=models.DecimalField(decimal_places=2, default=12, max_digits=5),
        ),
    ]
