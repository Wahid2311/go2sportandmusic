# Generated migration to add ticket_file field to Order model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_comprehensive_schema_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ticket_file',
            field=models.FileField(blank=True, null=True, upload_to='tickets/'),
        ),
    ]
