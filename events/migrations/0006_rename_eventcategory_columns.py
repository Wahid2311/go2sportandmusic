# Migration to rename EventCategory columns from created_at/updated_at to created/modified

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventcategory',
            old_name='created_at',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='eventcategory',
            old_name='updated_at',
            new_name='modified',
        ),
    ]
