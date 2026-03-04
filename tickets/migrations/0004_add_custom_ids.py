# Generated migration to add custom ID fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_add_ticket_file_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='ticket_number',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True),
        ),
    ]
