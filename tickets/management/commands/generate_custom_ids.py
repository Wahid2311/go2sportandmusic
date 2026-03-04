"""
Management command to generate custom IDs for existing tickets and orders
Run with: python manage.py generate_custom_ids
"""

from django.core.management.base import BaseCommand
from tickets.models import Ticket, Order
from tickets.id_generator import CustomIDGenerator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate custom IDs (Order# and Ticket#) for existing tickets and orders'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting custom ID generation...'))
        
        # Generate custom IDs for Tickets
        self.generate_ticket_ids()
        
        # Generate custom IDs for Orders
        self.generate_order_ids()
        
        self.stdout.write(self.style.SUCCESS('✓ Custom ID generation completed!'))

    def generate_ticket_ids(self):
        """Generate custom ticket numbers for existing tickets without them"""
        tickets_without_ids = Ticket.objects.filter(ticket_number__isnull=True) | Ticket.objects.filter(ticket_number='')
        count = tickets_without_ids.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No tickets need custom IDs'))
            return
        
        self.stdout.write(f'Generating custom IDs for {count} tickets...')
        
        updated = 0
        for ticket in tickets_without_ids:
            # Generate unique ticket number
            while True:
                ticket.ticket_number = CustomIDGenerator.generate_ticket_id()
                if not Ticket.objects.filter(ticket_number=ticket.ticket_number).exclude(id=ticket.id).exists():
                    break
            
            ticket.save()
            updated += 1
            
            if updated % 100 == 0:
                self.stdout.write(f'  ✓ Updated {updated}/{count} tickets')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated custom IDs for {updated} tickets'))

    def generate_order_ids(self):
        """Generate custom order numbers for existing orders without them"""
        orders_without_ids = Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number='')
        count = orders_without_ids.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No orders need custom IDs'))
            return
        
        self.stdout.write(f'Generating custom IDs for {count} orders...')
        
        updated = 0
        for order in orders_without_ids:
            # Generate unique order number
            while True:
                order.order_number = CustomIDGenerator.generate_order_id()
                if not Order.objects.filter(order_number=order.order_number).exclude(id=order.id).exists():
                    break
            
            order.save()
            updated += 1
            
            if updated % 100 == 0:
                self.stdout.write(f'  ✓ Updated {updated}/{count} orders')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated custom IDs for {updated} orders'))
