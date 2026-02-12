# This migration cleans up the broken migration history and resets the tickets app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        # This is a placeholder - the actual schema is already in the database
        # We just need to record that this migration has been applied
        migrations.RunPython(
            code=lambda apps, schema_editor: None,
            reverse_code=lambda apps, schema_editor: None,
        ),
    ]
