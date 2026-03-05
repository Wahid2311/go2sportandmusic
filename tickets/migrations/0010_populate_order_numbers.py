# Generated migration to populate order_number for all existing orders

from django.db import migrations
from tickets.id_generator import CustomIDGenerator


def populate_order_numbers(apps, schema_editor):
    """Populate order_number for all orders that don't have one"""
    Order = apps.get_model('tickets', 'Order')
    
    # Get all orders without order_number
    orders_without_number = Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number='')
    
    for order in orders_without_number:
        # Generate a unique order_number
        while True:
            new_order_number = CustomIDGenerator.generate_order_id()
            # Check if this order_number already exists
            if not Order.objects.filter(order_number=new_order_number).exists():
                order.order_number = new_order_number
                order.save(update_fields=['order_number'])
                break


def reverse_populate_order_numbers(apps, schema_editor):
    """Reverse: set order_number back to NULL"""
    Order = apps.get_model('tickets', 'Order')
    Order.objects.all().update(order_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_mark_stripe_fields_as_migrated'),
    ]

    operations = [
        migrations.RunPython(populate_order_numbers, reverse_populate_order_numbers),
    ]
