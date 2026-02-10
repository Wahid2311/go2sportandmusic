# Migration to add created_at and updated_at columns to EventCategory

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        # Add created_at column with default value
        migrations.AddField(
            model_name='eventcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add updated_at column with default value
        migrations.AddField(
            model_name='eventcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Remove old created column
        migrations.RemoveField(
            model_name='eventcategory',
            name='created',
        ),
        # Remove old modified column
        migrations.RemoveField(
            model_name='eventcategory',
            name='modified',
        ),
    ]
