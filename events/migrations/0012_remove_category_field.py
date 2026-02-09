# Migration to remove the problematic category field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_category_constraint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='category',
        ),
    ]
