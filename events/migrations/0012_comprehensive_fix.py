# Generated migration to fix EventCategory and category field issues

from django.db import migrations

def fix_eventcategory_and_category(apps, schema_editor):
    """Fix EventCategory data and make category field nullable"""
    EventCategory = apps.get_model('events', 'EventCategory')
    Event = apps.get_model('events', 'Event')
    
    try:
        # Ensure Football category exists
        football, created = EventCategory.objects.get_or_create(
            slug='football',
            defaults={
                'name': 'Football',
                'description': 'Football events',
                'icon': 'bi-soccer',
                'is_active': True,
                'order': 1
            }
        )
    except Exception as e:
        print(f"Error creating Football category: {e}")
    
    try:
        # Update all NULL categories to Football
        Event.objects.filter(category_legacy__isnull=True).update(category_legacy='Football')
    except Exception as e:
        print(f"Error updating NULL categories: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_category_constraint'),
    ]

    operations = [
        migrations.RunPython(fix_eventcategory_and_category),
    ]
