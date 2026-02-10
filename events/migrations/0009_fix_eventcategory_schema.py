# Migration to fix EventCategory schema - convert created/modified to created_at/updated_at

from django.db import migrations, models
import django.utils.timezone


def fix_schema(apps, schema_editor):
    """
    Safely migrate the EventCategory schema from created/modified to created_at/updated_at
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
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
            
            try:
                # Add new columns if they don't exist
                cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN created_at_new DATETIME DEFAULT CURRENT_TIMESTAMP")
                cursor.execute("ALTER TABLE events_eventcategory ADD COLUMN updated_at_new DATETIME DEFAULT CURRENT_TIMESTAMP")
                print("✓ Added new timestamp columns")
            except Exception as e:
                print(f"⚠ Could not add new columns (they might already exist): {e}")
            
            try:
                # Copy data from old columns to new columns
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET created_at_new = created, updated_at_new = modified
                    WHERE created_at_new IS NULL OR updated_at_new IS NULL
                """)
                print(f"✓ Copied data from old columns to new columns (affected: {cursor.rowcount} rows)")
            except Exception as e:
                print(f"⚠ Could not copy data: {e}")
        else:
            print(f"⚠ EventCategory schema is unclear. Columns: {columns}")


def reverse_fix(apps, schema_editor):
    """Reverse migration - not needed for this fix"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        # First, try to add the new columns using migrations
        migrations.AddField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
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
