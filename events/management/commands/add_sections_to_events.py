from django.core.management.base import BaseCommand
from events.models import Event, EventSection


class Command(BaseCommand):
    help = 'Add default sections to events that do not have any sections'

    def handle(self, *args, **options):
        # Get all events that don't have sections
        events_without_sections = Event.objects.filter(sections__isnull=True).distinct()
        
        if not events_without_sections.exists():
            self.stdout.write(self.style.SUCCESS('All events already have sections'))
            return
        
        default_sections = [
            {'name': 'General Admission', 'color': '#3CB44B', 'lower_price': 0, 'upper_price': 0},
            {'name': 'VIP', 'color': '#911EB4', 'lower_price': 0, 'upper_price': 0},
            {'name': 'Premium', 'color': '#F58231', 'lower_price': 0, 'upper_price': 0},
        ]
        
        count = 0
        for event in events_without_sections:
            for section_data in default_sections:
                EventSection.objects.create(
                    event=event,
                    name=section_data['name'],
                    color=section_data['color'],
                    lower_price=section_data['lower_price'],
                    upper_price=section_data['upper_price']
                )
            count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Added sections to event: {event.name} ({event.event_id})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added sections to {count} events'
            )
        )
