# Final merge migration to resolve all conflicts

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_fix_null_categories'),
        ('events', '0016_merge'),
        ('events', '0017_fix_eventcategory_columns'),
    ]

    operations = [
    ]
