# Merge migration to resolve conflicting 0013 migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_alter_category_nullable'),
        ('events', '0013_alter_category_nullable'),
    ]

    operations = [
    ]
