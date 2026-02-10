from django.db import migrations

def update_event_category(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    try:
        event = Event.objects.get(id='844bd416-3506-4226-b7e8-08c9949c4d7a')
        event.category_legacy = 'Formula 1'
        event.save()
        print(f"Updated event {event.id} category to Formula 1")
    except Event.DoesNotExist:
        print("Event not found")
    except Exception as e:
        print(f"Error: {e}")

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_comprehensive_fix'),
    ]

    operations = [
        migrations.RunPython(update_event_category, reverse_func),
    ]
