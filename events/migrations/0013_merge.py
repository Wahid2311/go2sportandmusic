# Merge migration to resolve conflicting migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_alter_category_nullable'),
    ]

    operations = [
    ]
