#!/usr/bin/env python3
"""
Automatic Listing Deletion Script
Deletes expired or sold-out tickets from the database
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

from tickets.models import Ticket
from events.models import Event
from django.utils import timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/listing_deletion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ListingDeletionManager:
    """Manages automatic deletion of expired or sold-out listings"""
    
    def __init__(self, delete_sold_out=True, days_after_expiry=7):
        """
        Initialize the listing deletion manager
        
        Args:
            delete_sold_out: Delete sold-out tickets (default: True)
            days_after_expiry: Days after event to delete (default: 7)
        """
        self.delete_sold_out = delete_sold_out
        self.days_after_expiry = days_after_expiry
        self.deleted_count = 0
        self.error_count = 0
    
    def get_expired_listings(self):
        """Get all listings that should be deleted"""
        try:
            expired_listings = []
            cutoff_date = timezone.now() - timedelta(days=self.days_after_expiry)
            
            # Get all tickets
            all_tickets = Ticket.objects.select_related('event')
            
            for ticket in all_tickets:
                should_delete = False
                
                # Check if event has passed
                if ticket.event and ticket.event.date < timezone.now():
                    should_delete = True
                
                # Check if sold out
                if self.delete_sold_out and ticket.sold:
                    should_delete = True
                
                # Check if number of tickets is 0
                if ticket.number_of_tickets <= 0:
                    should_delete = True
                
                if should_delete:
                    expired_listings.append(ticket)
            
            return expired_listings
        except Exception as e:
            logger.error(f"Error fetching expired listings: {str(e)}")
            traceback.print_exc()
            return []
    
    def delete_listing(self, ticket):
        """Delete a single listing"""
        try:
            ticket_id = ticket.ticket_id
            event_name = ticket.event.name if ticket.event else "Unknown Event"
            section = ticket.section.name if ticket.section else "Unknown Section"
            
            # Store info before deletion
            reason = []
            if ticket.event and ticket.event.date < timezone.now():
                reason.append("Event expired")
            if self.delete_sold_out and ticket.sold:
                reason.append("Sold out")
            if ticket.number_of_tickets <= 0:
                reason.append("No tickets available")
            
            reason_str = ", ".join(reason)
            
            # Delete the ticket
            ticket.delete()
            
            logger.info(f"✓ Deleted listing: {ticket_id} ({event_name} - {section}) - Reason: {reason_str}")
            self.deleted_count += 1
            
            return True
        except Exception as e:
            logger.error(f"✗ Error deleting listing {ticket.ticket_id}: {str(e)}")
            traceback.print_exc()
            self.error_count += 1
            return False
    
    def run(self):
        """Run the automatic listing deletion"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Automatic Listing Deletion")
            logger.info(f"Delete sold out: {self.delete_sold_out}")
            logger.info(f"Days after expiry: {self.days_after_expiry}")
            logger.info("=" * 60)
            
            expired_listings = self.get_expired_listings()
            
            if not expired_listings:
                logger.info("No expired listings found for deletion")
                return
            
            logger.info(f"Found {len(expired_listings)} expired listings to delete")
            
            for listing in expired_listings:
                self.delete_listing(listing)
            
            logger.info("=" * 60)
            logger.info(f"Listing Deletion Complete")
            logger.info(f"✓ Deleted: {self.deleted_count}")
            logger.info(f"✗ Errors: {self.error_count}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error in listing deletion: {str(e)}")
            traceback.print_exc()


def main():
    """Main entry point"""
    try:
        manager = ListingDeletionManager(delete_sold_out=True, days_after_expiry=7)
        manager.run()
    except Exception as e:
        logger.error(f"Failed to run listing deletion: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
