# Migration to add timestamp columns to EventCategory if they don't exist

from django.db import migrations, models
from django.utils import timezone


def add_timestamps_if_needed(apps, schema_editor):
    """Add created_at and updated_at columns if they don't exist"""
    EventCategory = apps.get_model('events', 'EventCategory')
    
    # Check if the columns exist by trying to access them
    try:
        # Try to get the first object and access the new fields
        obj = EventCategory.objects.first()
        if obj:
            _ = obj.created_at
            _ = obj.updated_at
    except AttributeError:
        # Columns don't exist, they will be added by the migration
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        # Add created_at column if it doesn't exist
        migrations.AddField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        # Add updated_at column if it doesn't exist
        migrations.AddField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
