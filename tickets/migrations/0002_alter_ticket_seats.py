from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='seats',
            field=ArrayField(base_field=models.CharField(max_length=10), blank=True, default=list, help_text='Comma separated seat numbers.', null=True, size=None),
        ),
    ]
