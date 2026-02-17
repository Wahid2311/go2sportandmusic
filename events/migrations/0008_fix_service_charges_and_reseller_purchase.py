# Generated migration to fix service charges and reseller purchase permissions

from django.db import migrations


def fix_service_charges(apps, schema_editor):
    """Set correct service charges: 20% for normal, 12% for reseller"""
    Event = apps.get_model('events', 'Event')
    
    # Update all events with correct service charges
    Event.objects.all().update(
        normal_service_charge=20,  # 20% for normal users
        reseller_service_charge=12  # 12% for resellers
    )
    
    print("✓ Updated service charges: Normal=20%, Reseller=12%")


def reverse_fix(apps, schema_editor):
    """Reverse operation"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_reset_migration_history'),
    ]

    operations = [
        migrations.RunPython(fix_service_charges, reverse_fix),
    ]
