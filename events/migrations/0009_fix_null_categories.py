# Migration to fix NULL category values - now handled by migration 0014
# This migration is kept for compatibility but is now a no-op

from django.db import migrations


def fix_null_categories(apps, schema_editor):
    """This is now handled by migration 0014_fix_eventcategory_schema"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_service_charge_limit'),
    ]

    operations = [
        migrations.RunPython(fix_null_categories, migrations.RunPython.noop),
    ]
