# Migration to update all existing events with correct service charges

from django.db import migrations


def update_service_charges(apps, schema_editor):
    """Update all existing events with correct service charges"""
    Event = apps.get_model('events', 'Event')
    Ticket = apps.get_model('tickets', 'Ticket')
    
    # Update all events to have 20% for normal and 12% for reseller
    Event.objects.all().update(
        normal_service_charge=20,
        reseller_service_charge=12
    )
    
    # Recalculate all ticket prices
    for ticket in Ticket.objects.all():
        ticket.save()


def reverse_update(apps, schema_editor):
    """Reverse the update (optional)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_comprehensive_schema_fix'),
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_service_charges, reverse_update),
    ]
