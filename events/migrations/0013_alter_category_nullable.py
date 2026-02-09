# Migration to make category field nullable since we're using category_legacy instead

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_remove_category_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(blank=True, choices=[('concert', 'Concert'), ('sports', 'Sports'), ('theater', 'Theater'), ('conference', 'Conference'), ('festival', 'Festival'), ('other', 'Other')], max_length=20, null=True),
        ),
    ]
