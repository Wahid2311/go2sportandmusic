# Migration to fix NULL category values

from django.db import migrations


def fix_null_categories(apps, schema_editor):
    """Set all NULL categories to Football (id=1)"""
    Event = apps.get_model('events', 'Event')
    EventCategory = apps.get_model('events', 'EventCategory')
    
    # Get or create Football category
    football, created = EventCategory.objects.get_or_create(
        slug='football',
        defaults={
            'name': 'Football',
            'description': 'Football events',
            'icon': 'bi-soccer',
            'is_active': True,
            'order': 1
        }
    )
    
    # Update all NULL categories to Football
    Event.objects.filter(category__isnull=True).update(category=football)


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(fix_null_categories),
    ]
