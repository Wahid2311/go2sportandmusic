"""
Management command to populate event categories from xs2events portal
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from events.models import EventCategory


class Command(BaseCommand):
    help = 'Populate event categories from xs2events portal'

    def handle(self, *args, **options):
        # Categories from xs2events portal
        categories_data = [
            {
                'name': 'Football',
                'icon': 'bi-soccer',
                'order': 1
            },
            {
                'name': 'Formula 1',
                'icon': 'bi-speedometer2',
                'order': 2
            },
            {
                'name': 'MotoGP',
                'icon': 'bi-speedometer2',
                'order': 3
            },
            {
                'name': 'Tennis',
                'icon': 'bi-racquet',
                'order': 4
            },
            {
                'name': 'Other events',
                'icon': 'bi-calendar-event',
                'order': 5
            },
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            slug = slugify(cat_data['name'])
            category, created = EventCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                # Update existing category
                category.name = cat_data['name']
                category.icon = cat_data['icon']
                category.order = cat_data['order']
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} categories and updated {updated_count} categories'
            )
        )
