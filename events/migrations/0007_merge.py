# Merge migration to resolve conflicting migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_fix_eventcategory_table'),
        ('events', '0006_rename_eventcategory_fields'),
    ]

    operations = [
    ]
