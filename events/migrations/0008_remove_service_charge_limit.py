# Migration to remove the 100 limit on service charge fields

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_set_default_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='normal_service_charge',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                help_text='Service charge for normal users (no maximum limit)'
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='reseller_service_charge',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                help_text='Service charge for resellers (no maximum limit)'
            ),
        ),
    ]
