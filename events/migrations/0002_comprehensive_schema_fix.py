# Generated migration to fix all schema issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
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
    ]
