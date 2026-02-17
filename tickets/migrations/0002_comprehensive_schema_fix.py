# Generated migration to fix all schema issues in tickets app

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        # Fix the Ticket model to have proper fields
        migrations.AlterField(
            model_name='ticket',
            name='seats',
            field=models.JSONField(default=list, blank=True),
        ),
    ]
