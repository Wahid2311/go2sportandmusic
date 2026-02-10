from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_comprehensive_fix'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE events_event SET category_legacy = 'Formula 1' WHERE id = '844bd416-3506-4226-b7e8-08c9949c4d7a'",
            "UPDATE events_event SET category_legacy = 'Other' WHERE id = '844bd416-3506-4226-b7e8-08c9949c4d7a'"
        ),
    ]
