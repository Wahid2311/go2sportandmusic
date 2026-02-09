# Merge migration to resolve conflict between 0009 versions

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_fix_null_categories'),
        ('events', '0015_merge_all'),
    ]

    operations = [
    ]
