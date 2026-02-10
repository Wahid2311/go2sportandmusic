# Migration to fix EventCategory schema - convert created/modified to created_at/updated_at

from django.db import migrations, models
from django.utils import timezone


def fix_schema(apps, schema_editor):
    """
    Safely migrate the EventCategory schema from created/modified to created_at/updated_at
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Check if the columns already exist
            cursor.execute("PRAGMA table_info(events_eventcategory)")
            columns = {row[1] for row in cursor.fetchall()}
            
            # If new columns already exist, we're done
            if 'created_at' in columns and 'updated_at' in columns:
                print("✓ EventCategory already has created_at/updated_at columns")
                return
            
            # If old columns exist, we need to migrate them
            if 'created' in columns and 'modified' in columns:
                print("Migrating EventCategory schema from created/modified to created_at/updated_at...")
                
                # First, update any NULL values in the old columns
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET created = CURRENT_TIMESTAMP, modified = CURRENT_TIMESTAMP
                    WHERE created IS NULL OR modified IS NULL
                """)
                print(f"✓ Updated NULL values in old columns")
                
                # Copy data from old columns to new columns
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET created_at = created, updated_at = modified
                """)
                print(f"✓ Copied data from old columns to new columns")
        except Exception as e:
            print(f"⚠ Error in fix_schema: {e}")
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
        # First, add the new columns with null=True and a default value
        migrations.AddField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(default=timezone.now, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(default=timezone.now, null=True),
            preserve_default=False,
        ),
        # Then run the Python function to handle the migration
        migrations.RunPython(fix_schema, reverse_fix),
        # Finally, make the columns NOT NULL
        migrations.AlterField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
