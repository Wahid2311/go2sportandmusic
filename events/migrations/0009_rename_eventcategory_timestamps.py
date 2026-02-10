# Migration to rename created/modified columns to created_at/updated_at in EventCategory

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventcategory',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='eventcategory',
            old_name='modified',
            new_name='updated_at',
        ),
    ]
