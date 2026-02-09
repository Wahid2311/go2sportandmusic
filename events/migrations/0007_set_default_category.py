# Migration to set default category for existing events

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
        # First, set all null categories to Football (id=1)
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model('events', 'Event').objects.filter(category__isnull=True).update(category_id=1),
            reverse_code=migrations.RunPython.noop,
        ),
        # Then update the field to not allow null
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='events.eventcategory'),
        ),
    ]
