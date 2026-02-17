# Generated migration to fix all schema issues

from django.db import migrations, models
import django.utils.timezone


def fix_event_schema(apps, schema_editor):
    """Fix the Event model schema"""
    Event = apps.get_model('events', 'Event')
    
    # Set default service charges for all events
    for event in Event.objects.all():
        if event.normal_service_charge is None or event.normal_service_charge == 0:
            event.normal_service_charge = 20
        if event.reseller_service_charge is None or event.reseller_service_charge == 0:
            event.reseller_service_charge = 12
        event.save()


def fix_eventcategory_schema(apps, schema_editor):
    """Fix the EventCategory model schema"""
    EventCategory = apps.get_model('events', 'EventCategory')
    now = django.utils.timezone.now()
    
    # Add created and updated timestamps to existing categories
    for category in EventCategory.objects.all():
        if not hasattr(category, 'created') or category.created is None:
            category.created = now
        if not hasattr(category, 'updated') or category.updated is None:
            category.updated = now
        category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        # Add created field to EventCategory
        migrations.AddField(
            model_name='eventcategory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add updated field to EventCategory
        migrations.AddField(
            model_name='eventcategory',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        # Set default service charges for Event model
        migrations.AlterField(
            model_name='event',
            name='normal_service_charge',
            field=models.IntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='reseller_service_charge',
            field=models.IntegerField(default=12),
        ),
        # Run Python code to fix existing data
        migrations.RunPython(fix_event_schema),
        migrations.RunPython(fix_eventcategory_schema),
    ]
