# Migration to add created_at and updated_at columns to EventCategory

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_fix_database_schema'),
    ]

    operations = [
        # Add created_at and updated_at columns
        migrations.AddField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
