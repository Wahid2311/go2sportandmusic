from django.core.management.base import BaseCommand
from events.models import EventCategory

class Command(BaseCommand):
    help = 'Fix the Football and Tennis category icons'

    def handle(self, *args, **options):
        # Fix Football icon
        football = EventCategory.objects.filter(slug='football').first()
        if football:
            football.icon = 'bi-football'
            football.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Football icon to bi-football'))

        # Fix Tennis icon
        tennis = EventCategory.objects.filter(slug='tennis').first()
        if tennis:
            tennis.icon = 'bi-tennis'
            tennis.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Tennis icon to bi-tennis'))

        self.stdout.write(self.style.SUCCESS('Category icons fixed successfully!'))
