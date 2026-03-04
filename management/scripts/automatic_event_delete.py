#!/usr/bin/env python3
"""
Automatic Event Deletion Script
Deletes expired events from the database based on event date
"""

import os
import sys
import django
import traceback
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from events.models import Event
from django.utils import timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/event_deletion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EventDeletionManager:
    """Manages automatic deletion of expired events"""
    
    def __init__(self, days_after_expiry=30):
        """
        Initialize the event deletion manager
        
        Args:
            days_after_expiry: Number of days after event date to delete (default: 30)
        """
        self.days_after_expiry = days_after_expiry
        self.deleted_count = 0
        self.error_count = 0
    
    def get_expired_events(self):
        """Get all events that should be deleted"""
        try:
            cutoff_date = timezone.now() - timedelta(days=self.days_after_expiry)
            expired_events = Event.objects.filter(
                date__lt=cutoff_date,
                is_active=True  # Only delete active events
            )
            return expired_events
        except Exception as e:
            logger.error(f"Error fetching expired events: {str(e)}")
            traceback.print_exc()
            return []
    
    def delete_event(self, event):
        """Delete a single event"""
        try:
            event_name = event.name
            event_id = event.id
            
            # Delete associated tickets first
            tickets = event.ticket_set.all()
            ticket_count = tickets.count()
            tickets.delete()
            
            # Delete the event
            event.delete()
            
            logger.info(f"✓ Deleted event: {event_name} (ID: {event_id}) with {ticket_count} tickets")
            self.deleted_count += 1
            
            return True
        except Exception as e:
            logger.error(f"✗ Error deleting event {event.name}: {str(e)}")
            traceback.print_exc()
            self.error_count += 1
            return False
    
    def run(self):
        """Run the automatic event deletion"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Automatic Event Deletion")
            logger.info(f"Deleting events older than {self.days_after_expiry} days")
            logger.info("=" * 60)
            
            expired_events = self.get_expired_events()
            
            if not expired_events.exists():
                logger.info("No expired events found for deletion")
                return
            
            logger.info(f"Found {expired_events.count()} expired events to delete")
            
            for event in expired_events:
                self.delete_event(event)
            
            logger.info("=" * 60)
            logger.info(f"Event Deletion Complete")
            logger.info(f"✓ Deleted: {self.deleted_count}")
            logger.info(f"✗ Errors: {self.error_count}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error in event deletion: {str(e)}")
            traceback.print_exc()


def main():
    """Main entry point"""
    try:
        manager = EventDeletionManager(days_after_expiry=30)
        manager.run()
    except Exception as e:
        logger.error(f"Failed to run event deletion: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
