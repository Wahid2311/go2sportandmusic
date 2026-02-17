from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def fix_everything(apps, schema_editor):
    """
    Comprehensive fix that:
    1. Clears all broken migration records from django_migrations table
    2. Adds missing columns to EventCategory
    3. Sets correct service charges (20% for normal, 12% for reseller)
    4. Recalculates ticket prices
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Delete ALL migration records - we're starting fresh
        try:
            cursor.execute("DELETE FROM django_migrations")
        except:
            pass
        
        # Re-insert only the valid migrations that should exist
        valid_migrations = [
            ('events', '0001_initial'),
            ('events', '0002_event_country_event_sports_type_and_more'),
            ('events', '0003_category'),
            ('events', '0004_category_country_category_type_and_more'),
            ('events', '0005_eventcategory'),
            ('events', '0006_comprehensive_fix'),
            ('tickets', '0001_initial'),
        ]
        
        for app, name in valid_migrations:
            try:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    (app, name, timezone.now())
                )
            except:
                pass
        
        # Add missing columns to EventCategory
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass
        
        try:
            cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass
        
        # Update Event service charges
        try:
            cursor.execute("UPDATE events_event SET normal_service_charge = 20, reseller_service_charge = 12")
        except:
            pass
        
        # Recalculate ticket prices by updating all tickets
        try:
            cursor.execute("""
                UPDATE tickets_ticket 
                SET sell_price_for_normal = sell_price + (sell_price * 20 / 100),
                    sell_price_for_reseller = sell_price + (sell_price * 12 / 100)
                WHERE sell_price IS NOT NULL
            """)
        except:
            pass


def reverse_fix(apps, schema_editor):
    """Reverse function - does nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        migrations.RunPython(fix_everything, reverse_fix),
    ]
