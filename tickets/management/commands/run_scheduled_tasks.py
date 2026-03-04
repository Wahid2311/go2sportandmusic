from django.core.management import call_command
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scheduler runner - runs update_payout_status command'
    
    def handle(self, *args, **options):
        try:
            call_command('update_payout_status')
            logger.info('Payout status update completed successfully')
        except Exception as e:
            logger.error(f'Error running payout status update: {str(e)}')
