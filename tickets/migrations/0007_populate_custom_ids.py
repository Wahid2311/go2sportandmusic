# Generated migration to populate ticket_number and order_number fields

from django.db import migrations
from tickets.id_generator import CustomIDGenerator


def populate_ids(apps, schema_editor):
    """Populate ticket_number and order_number for all existing records"""
    Ticket = apps.get_model('tickets', 'Ticket')
    Order = apps.get_model('tickets', 'Order')
    
    # Populate ticket_number for tickets without one
    tickets_without_number = Ticket.objects.filter(ticket_number__isnull=True) | Ticket.objects.filter(ticket_number='')
    for ticket in tickets_without_number:
        ticket.ticket_number = CustomIDGenerator.generate_ticket_id()
        ticket.save()
    
    # Populate order_number for orders without one
    orders_without_number = Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number='')
    for order in orders_without_number:
        order.order_number = CustomIDGenerator.generate_order_id()
        order.save()


def reverse_populate(apps, schema_editor):
    """Reverse operation - set custom IDs back to NULL"""
    # This is a data migration, so we don't reverse it
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_populate_ticket_numbers'),
    ]

    operations = [
        migrations.RunPython(populate_ids, reverse_populate),
    ]
