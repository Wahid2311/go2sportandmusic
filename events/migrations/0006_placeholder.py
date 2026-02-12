# Placeholder migration to fill gap in migration sequence

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        # No operations - this is just a placeholder to fill the gap in the migration sequence
    ]
