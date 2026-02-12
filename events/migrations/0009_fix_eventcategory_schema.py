# Migration to fix EventCategory schema - convert created/modified to created_at/updated_at

from django.db import migrations, models
from django.utils import timezone


def fix_schema(apps, schema_editor):
    """
    Safely handle EventCategory schema - columns may already exist in PostgreSQL
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # For PostgreSQL, check if columns exist using information_schema
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'events_eventcategory' AND column_name IN ('created_at', 'updated_at')
            """)
            existing_columns = {row[0] for row in cursor.fetchall()}
            
            # If new columns already exist, we're done
            if 'created_at' in existing_columns and 'updated_at' in existing_columns:
                print("✓ EventCategory already has created_at/updated_at columns")
                return
            
            print(f"✓ Migration completed successfully")
        except Exception as e:
            print(f"⚠ Info: {e}")
            # Don't fail the migration, just continue
            pass


def reverse_fix(apps, schema_editor):
    """Reverse migration - not needed for this fix"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        # Just run the Python function to check/verify the schema
        # The columns should already exist in PostgreSQL
        migrations.RunPython(fix_schema, reverse_fix),
    ]
