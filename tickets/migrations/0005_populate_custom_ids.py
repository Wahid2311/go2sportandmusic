# Data migration to populate custom IDs for existing tickets and orders

from django.db import migrations
import random
import string


def generate_ticket_id():
    """Generate a unique 9-digit ticket ID"""
    return ''.join(random.choices(string.digits, k=9))


def generate_order_id():
    """Generate a unique 9-digit order ID"""
    return ''.join(random.choices(string.digits, k=9))


def populate_ticket_ids(apps, schema_editor):
    """Populate ticket_number for all existing tickets"""
    Ticket = apps.get_model('tickets', 'Ticket')
    
    for ticket in Ticket.objects.filter(ticket_number__isnull=True) | Ticket.objects.filter(ticket_number=''):
        # Generate unique ticket number
        while True:
            ticket.ticket_number = generate_ticket_id()
            if not Ticket.objects.filter(ticket_number=ticket.ticket_number).exclude(id=ticket.id).exists():
                break
        ticket.save()


def populate_order_ids(apps, schema_editor):
    """Populate order_number for all existing orders"""
    Order = apps.get_model('tickets', 'Order')
    
    for order in Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number=''):
        # Generate unique order number
        while True:
            order.order_number = generate_order_id()
            if not Order.objects.filter(order_number=order.order_number).exclude(id=order.id).exists():
                break
        order.save()


def reverse_populate(apps, schema_editor):
    """Reverse migration - clear the custom IDs"""
    Ticket = apps.get_model('tickets', 'Ticket')
    Order = apps.get_model('tickets', 'Order')
    
    Ticket.objects.all().update(ticket_number=None)
    Order.objects.all().update(order_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_add_custom_ids'),
    ]

    operations = [
        migrations.RunPython(populate_ticket_ids, reverse_populate),
        migrations.RunPython(populate_order_ids, reverse_populate),
    ]
