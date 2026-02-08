# Final fix migration - explicitly depends on 0005 to bypass problematic migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_eventcategory'),
    ]

    operations = [
    ]
