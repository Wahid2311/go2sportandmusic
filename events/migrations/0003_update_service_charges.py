# Migration to update existing events with correct service charges

from django.db import migrations


def update_service_charges(apps, schema_editor):
    """Update all existing events with correct service charges"""
    Event = apps.get_model('events', 'Event')
    
    # Update all events with correct service charges
    events_updated = Event.objects.filter(
        normal_service_charge__isnull=True
    ) | Event.objects.filter(
        reseller_service_charge__isnull=True
    )
    
    for event in events_updated:
        if event.normal_service_charge is None:
            event.normal_service_charge = 20
        if event.reseller_service_charge is None:
            event.reseller_service_charge = 12
        event.save()
    
    # Also update any events that have incorrect values
    Event.objects.exclude(
        normal_service_charge=20,
        reseller_service_charge=12
    ).update(
        normal_service_charge=20,
        reseller_service_charge=12
    )


def reverse_update(apps, schema_editor):
    """Reverse the update (set to None)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_comprehensive_schema_fix'),
    ]

    operations = [
        migrations.RunPython(update_service_charges, reverse_update),
    ]
