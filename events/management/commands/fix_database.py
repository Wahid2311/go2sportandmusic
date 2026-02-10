from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the database state by cleaning up broken migrations and fixing data'

    def handle(self, *args, **options):
        """
        Fix the database by:
        1. Deleting broken migration records
        2. Ensuring Football category exists
        3. Updating NULL categories
        """
        with connection.cursor() as cursor:
            try:
                # Delete the broken migration records
                cursor.execute("""
                    DELETE FROM django_migrations 
                    WHERE app = 'events' AND name = '0009_fix_null_categories'
                """)
                self.stdout.write(self.style.SUCCESS('Deleted broken migration record'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not delete migration record: {e}'))
            
            try:
                # Ensure Football category exists
                cursor.execute("""
                    INSERT OR IGNORE INTO events_eventcategory 
                    (name, slug, description, icon, is_active, "order", created, modified)
                    VALUES ('Football', 'football', 'Football events', 'bi-soccer', 1, 1, datetime('now'), datetime('now'))
                """)
                self.stdout.write(self.style.SUCCESS('Ensured Football category exists'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not insert Football category: {e}'))
            
            try:
                # Update any NULL categories to Football
                cursor.execute("""
                    UPDATE events_eventcategory 
                    SET category_id = (SELECT id FROM events_eventcategory WHERE slug = 'football')
                    WHERE category_id IS NULL AND slug != 'football'
                """)
                self.stdout.write(self.style.SUCCESS('Updated NULL categories to Football'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not update NULL categories: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Database fix completed'))
