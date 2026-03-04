"""
Management command to release expired ticket reservations.
This should be run periodically (e.g., every minute) via a cron job or task scheduler.

Usage:
    python manage.py release_expired_reservations
"""

from django.core.management.base import BaseCommand
from tickets.reservation_utils import release_expired_reservations
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Release expired ticket reservations (older than 10 minutes)'

    def handle(self, *args, **options):
        try:
            count = release_expired_reservations()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully released {count} expired ticket reservations'
                )
            )
            logger.info(f'Released {count} expired ticket reservations')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error releasing expired reservations: {str(e)}')
            )
            logger.error(f'Error releasing expired reservations: {str(e)}')
