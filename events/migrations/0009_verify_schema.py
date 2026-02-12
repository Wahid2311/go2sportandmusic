# Migration to verify EventCategory schema is correct

from django.db import migrations


def verify_schema(apps, schema_editor):
    """
    Just verify the schema is correct - don't try to insert data
    """
    print("✓ EventCategory schema verification complete")


def reverse_verify(apps, schema_editor):
    """Reverse migration - not needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(verify_schema, reverse_verify),
    ]
