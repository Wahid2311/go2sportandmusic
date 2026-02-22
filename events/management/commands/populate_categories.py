"""
Management command to populate event categories from xs2events portal
"""
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from events.models import EventCategory


class Command(BaseCommand):
    help = 'Populate event categories from xs2events portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-url',
            type=str,
            default='https://api.xs2events.com/categories',
            help='xs2events API URL for fetching categories'
        )

    def fetch_from_api(self, api_url):
        """Fetch categories from xs2events API"""
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.stdout.write(
                self.style.WARNING(
                    f'Failed to fetch categories from API ({api_url}): {str(e)}'
                )
            )
            return None

    def get_default_categories(self):
        """Return default categories if API is not available"""
        return [
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

    def handle(self, *args, **options):
        api_url = options.get('api_url')
        
        # Try to fetch from API first
        categories_data = self.fetch_from_api(api_url)
        
        # If API fails, use default categories
        if not categories_data:
            self.stdout.write(
                self.style.WARNING('Using default categories')
            )
            categories_data = self.get_default_categories()

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            # Handle both API response format and default format
            name = cat_data.get('name') or cat_data.get('title')
            icon = cat_data.get('icon', 'bi-calendar-event')
            order = cat_data.get('order', 0)
            
            if not name:
                continue
                
            slug = slugify(name)
            category, created = EventCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'icon': icon,
                    'order': order,
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
                category.name = name
                category.icon = icon
                category.order = order
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
