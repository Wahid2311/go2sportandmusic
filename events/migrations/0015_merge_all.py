# Merge migration to resolve all conflicting branches

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_final_fix'),
        ('events', '0013_merge'),
        ('events', '0014_merge'),
    ]

    operations = [
    ]
