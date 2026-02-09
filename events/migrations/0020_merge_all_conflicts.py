# FINAL merge migration to resolve ALL conflicting branches

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_final_fix'),
        ('events', '0013_merge'),
        ('events', '0014_merge'),
        ('events', '0019_fix_columns'),
    ]

    operations = [
    ]
