from django.db import migrations
from tickets.id_generator import CustomIDGenerator

def populate_ticket_numbers(apps, schema_editor):
    """Populate ticket_number for all existing tickets"""
    Ticket = apps.get_model('tickets', 'Ticket')
    for ticket in Ticket.objects.filter(ticket_number__isnull=True):
        ticket.ticket_number = CustomIDGenerator.generate_ticket_id()
        ticket.save(update_fields=['ticket_number'])

def populate_order_numbers(apps, schema_editor):
    """Populate order_number for all existing orders"""
    Order = apps.get_model('tickets', 'Order')
    for order in Order.objects.filter(order_number__isnull=True):
        order.order_number = CustomIDGenerator.generate_order_id()
        order.save(update_fields=['order_number'])

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
        migrations.RunPython(populate_ticket_numbers, reverse_populate),
        migrations.RunPython(populate_order_numbers, reverse_populate),
    ]
