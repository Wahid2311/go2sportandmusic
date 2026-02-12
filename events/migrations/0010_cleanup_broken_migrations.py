# Migration to clean up broken migration history

from django.db import migrations, connection


def cleanup_migrations(apps, schema_editor):
    """Delete broken migration records from the database"""
    with connection.cursor() as cursor:
        # Delete all problematic migrations
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'events' AND (
                name LIKE '0009_%' OR
                name LIKE '0010_%' OR
                name LIKE '0011_%' OR
                name LIKE '0012_%' OR
                name LIKE '0013_%' OR
                name LIKE '0014_%' OR
                name LIKE '0015_%' OR
                name LIKE '0016_%' OR
                name LIKE '0017_%' OR
                name LIKE '0018_%' OR
                name LIKE '0019_%'
            )
        """)
        
        # Delete all problematic migrations from tickets app
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'tickets' AND (
                name = '0002_alter_ticket_upload_file' OR
                name = '0003_ticket_bundle_id_ticket_sell_together' OR
                name = '0004_stripe_fields' OR
                name = '0005_alter_ticket_upload_file' OR
                name LIKE '0006_%' OR 
                name LIKE '0007_%' OR 
                name LIKE '0008_%' OR 
                name LIKE '0009_%' OR 
                name LIKE '0010_%'
            )
        """)
        
        print("✓ Cleaned up broken migration records")


def reverse_cleanup(apps, schema_editor):
    """Reverse operation (do nothing)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_set_default_category'),
    ]

    operations = [
        migrations.RunPython(cleanup_migrations, reverse_cleanup),
    ]
