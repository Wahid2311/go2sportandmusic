#!/usr/bin/env python3
"""
Checking Utility Script
Verifies data integrity and generates reports on events, listings, and sales
"""

import os
import sys
import django
import traceback
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from events.models import Event, Category
from tickets.models import Ticket, Order, Sale
from django.utils import timezone
from django.db.models import Sum, Count, Q

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/checking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataChecker:
    """Checks data integrity and generates reports"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def check_events(self):
        """Check event data integrity"""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING EVENTS")
        logger.info("=" * 60)
        
        try:
            total_events = Event.objects.count()
            active_events = Event.objects.filter(is_active=True).count()
            expired_events = Event.objects.filter(date__lt=timezone.now()).count()
            upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
            
            self.stats['total_events'] = total_events
            self.stats['active_events'] = active_events
            self.stats['expired_events'] = expired_events
            self.stats['upcoming_events'] = upcoming_events
            
            logger.info(f"Total Events: {total_events}")
            logger.info(f"Active Events: {active_events}")
            logger.info(f"Expired Events: {expired_events}")
            logger.info(f"Upcoming Events: {upcoming_events}")
            
            # Check for events without categories
            events_no_category = Event.objects.filter(category__isnull=True).count()
            if events_no_category > 0:
                self.warnings.append(f"{events_no_category} events without category")
                logger.warning(f"⚠ {events_no_category} events without category")
            
            # Check for events without dates
            events_no_date = Event.objects.filter(date__isnull=True).count()
            if events_no_date > 0:
                self.issues.append(f"{events_no_date} events without date")
                logger.error(f"✗ {events_no_date} events without date")
            
            # Check for events without names
            events_no_name = Event.objects.filter(name__isnull=True).count()
            if events_no_name > 0:
                self.issues.append(f"{events_no_name} events without name")
                logger.error(f"✗ {events_no_name} events without name")
            
            logger.info("✓ Event check complete")
            
        except Exception as e:
            logger.error(f"Error checking events: {str(e)}")
            traceback.print_exc()
    
    def check_listings(self):
        """Check ticket listing data integrity"""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING LISTINGS")
        logger.info("=" * 60)
        
        try:
            total_listings = Ticket.objects.count()
            active_listings = Ticket.objects.filter(sold=False).count()
            sold_listings = Ticket.objects.filter(sold=True).count()
            
            self.stats['total_listings'] = total_listings
            self.stats['active_listings'] = active_listings
            self.stats['sold_listings'] = sold_listings
            
            logger.info(f"Total Listings: {total_listings}")
            logger.info(f"Active Listings: {active_listings}")
            logger.info(f"Sold Listings: {sold_listings}")
            
            # Check for listings with 0 tickets
            zero_tickets = Ticket.objects.filter(number_of_tickets=0).count()
            if zero_tickets > 0:
                self.warnings.append(f"{zero_tickets} listings with 0 tickets")
                logger.warning(f"⚠ {zero_tickets} listings with 0 tickets")
            
            # Check for listings without events
            listings_no_event = Ticket.objects.filter(event__isnull=True).count()
            if listings_no_event > 0:
                self.issues.append(f"{listings_no_event} listings without event")
                logger.error(f"✗ {listings_no_event} listings without event")
            
            # Check for listings without sections
            listings_no_section = Ticket.objects.filter(section__isnull=True).count()
            if listings_no_section > 0:
                self.warnings.append(f"{listings_no_section} listings without section")
                logger.warning(f"⚠ {listings_no_section} listings without section")
            
            # Total tickets available
            total_tickets = Ticket.objects.aggregate(Sum('number_of_tickets'))['number_of_tickets__sum'] or 0
            self.stats['total_tickets_available'] = total_tickets
            logger.info(f"Total Tickets Available: {total_tickets}")
            
            logger.info("✓ Listing check complete")
            
        except Exception as e:
            logger.error(f"Error checking listings: {str(e)}")
            traceback.print_exc()
    
    def check_sales(self):
        """Check sales and order data integrity"""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING SALES & ORDERS")
        logger.info("=" * 60)
        
        try:
            total_orders = Order.objects.count()
            total_sales = Sale.objects.count()
            
            # Sales statistics
            processing_sales = Sale.objects.filter(payout_status='processing').count()
            completed_sales = Sale.objects.filter(payout_status='completed').count()
            
            self.stats['total_orders'] = total_orders
            self.stats['total_sales'] = total_sales
            self.stats['processing_sales'] = processing_sales
            self.stats['completed_sales'] = completed_sales
            
            logger.info(f"Total Orders: {total_orders}")
            logger.info(f"Total Sales: {total_sales}")
            logger.info(f"Processing Sales: {processing_sales}")
            logger.info(f"Completed Sales: {completed_sales}")
            
            # Revenue statistics
            total_revenue = Sale.objects.aggregate(Sum('amount'))['amount__sum'] or 0
            self.stats['total_revenue'] = total_revenue
            logger.info(f"Total Revenue: £{total_revenue:.2f}")
            
            # Check for orders without buyers
            orders_no_buyer = Order.objects.filter(buyer__isnull=True).count()
            if orders_no_buyer > 0:
                self.issues.append(f"{orders_no_buyer} orders without buyer")
                logger.error(f"✗ {orders_no_buyer} orders without buyer")
            
            # Check for sales without orders
            sales_no_order = Sale.objects.filter(order__isnull=True).count()
            if sales_no_order > 0:
                self.issues.append(f"{sales_no_order} sales without order")
                logger.error(f"✗ {sales_no_order} sales without order")
            
            # Check for unpaid sales
            unpaid_sales = Sale.objects.filter(paid_to_reseller=False).count()
            if unpaid_sales > 0:
                logger.warning(f"⚠ {unpaid_sales} unpaid sales")
            
            logger.info("✓ Sales check complete")
            
        except Exception as e:
            logger.error(f"Error checking sales: {str(e)}")
            traceback.print_exc()
    
    def check_categories(self):
        """Check category data"""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING CATEGORIES")
        logger.info("=" * 60)
        
        try:
            total_categories = Category.objects.count()
            self.stats['total_categories'] = total_categories
            
            logger.info(f"Total Categories: {total_categories}")
            
            # Category breakdown
            category_stats = Category.objects.annotate(
                event_count=Count('event')
            ).values('name', 'event_count').order_by('-event_count')
            
            logger.info("\nCategory Breakdown:")
            for cat in category_stats:
                logger.info(f"  {cat['name']}: {cat['event_count']} events")
            
            logger.info("✓ Category check complete")
            
        except Exception as e:
            logger.error(f"Error checking categories: {str(e)}")
            traceback.print_exc()
    
    def generate_report(self):
        """Generate comprehensive report"""
        logger.info("\n" + "=" * 60)
        logger.info("DATA INTEGRITY REPORT")
        logger.info("=" * 60)
        logger.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Statistics
        logger.info("\nSTATISTICS:")
        for key, value in self.stats.items():
            if isinstance(value, float):
                logger.info(f"  {key}: £{value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Issues
        if self.issues:
            logger.error("\nCRITICAL ISSUES:")
            for issue in self.issues:
                logger.error(f"  ✗ {issue}")
        else:
            logger.info("\n✓ No critical issues found")
        
        # Warnings
        if self.warnings:
            logger.warning("\nWARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  ⚠ {warning}")
        else:
            logger.info("✓ No warnings")
        
        logger.info("\n" + "=" * 60)
        logger.info("REPORT COMPLETE")
        logger.info("=" * 60)
    
    def run(self):
        """Run all checks"""
        try:
            logger.info("\n" + "=" * 60)
            logger.info("STARTING DATA INTEGRITY CHECK")
            logger.info("=" * 60)
            
            self.check_events()
            self.check_listings()
            self.check_sales()
            self.check_categories()
            self.generate_report()
            
        except Exception as e:
            logger.error(f"Fatal error in data checker: {str(e)}")
            traceback.print_exc()


def main():
    """Main entry point"""
    try:
        checker = DataChecker()
        checker.run()
    except Exception as e:
        logger.error(f"Failed to run data checker: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
