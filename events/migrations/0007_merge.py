# Merge migration to resolve conflicting migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_fix_eventcategory_table'),
    ]

    operations = [
    ]
