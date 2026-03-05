from django.core.management.base import BaseCommand
from tickets.models import Ticket, Order
from tickets.id_generator import CustomIDGenerator


class Command(BaseCommand):
    help = 'Populate ticket_number and order_number for all existing records'

    def handle(self, *args, **options):
        # Populate ticket_number for tickets without one
        tickets_without_number = Ticket.objects.filter(ticket_number__isnull=True) | Ticket.objects.filter(ticket_number='')
        count_tickets = 0
        for ticket in tickets_without_number:
            ticket.ticket_number = CustomIDGenerator.generate_ticket_id()
            ticket.save()
            count_tickets += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {count_tickets} tickets with ticket_number'))

        # Populate order_number for orders without one
        orders_without_number = Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number='')
        count_orders = 0
        for order in orders_without_number:
            order.order_number = CustomIDGenerator.generate_order_id()
            order.save()
            count_orders += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {count_orders} orders with order_number'))
        self.stdout.write(self.style.SUCCESS('All IDs have been populated successfully!'))
