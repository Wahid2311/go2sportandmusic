# Migration to safely handle duplicate stripe columns that may already exist

from django.db import migrations, models


def safe_add_fields(apps, schema_editor):
    """Safely add fields if they don't already exist"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tickets_order' 
            AND column_name IN ('stripe_payment_intent_id', 'stripe_session_id')
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # Add stripe_payment_intent_id if it doesn't exist
        if 'stripe_payment_intent_id' not in existing_columns:
            cursor.execute("""
                ALTER TABLE tickets_order 
                ADD COLUMN stripe_payment_intent_id varchar(255) NULL
            """)
        
        # Add stripe_session_id if it doesn't exist
        if 'stripe_session_id' not in existing_columns:
            cursor.execute("""
                ALTER TABLE tickets_order 
                ADD COLUMN stripe_session_id varchar(255) NULL
            """)


def reverse_safe_add_fields(apps, schema_editor):
    """Reverse operation - do nothing since we're just fixing existing state"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_fix_stripe_fields_sqlite'),
    ]

    operations = [
        migrations.RunPython(safe_add_fields, reverse_safe_add_fields),
    ]
