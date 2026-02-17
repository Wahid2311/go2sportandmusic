# Generated migration to recalculate ticket prices based on updated service charges

from django.db import migrations


def recalculate_prices(apps, schema_editor):
    """Recalculate all ticket prices based on the event's service charges"""
    Ticket = apps.get_model('tickets', 'Ticket')
    
    for ticket in Ticket.objects.all():
        normal_charge = ticket.event.normal_service_charge or 0
        reseller_charge = ticket.event.reseller_service_charge or 0
        
        ticket.sell_price_for_normal = ticket.sell_price + (((ticket.sell_price * normal_charge) / 100) or 0)
        ticket.sell_price_for_reseller = ticket.sell_price + (((ticket.sell_price * reseller_charge) / 100) or 0)
        ticket.save(update_fields=['sell_price_for_normal', 'sell_price_for_reseller'])
    
    print(f"✓ Recalculated prices for {Ticket.objects.count()} tickets")


def reverse_calc(apps, schema_editor):
    """Reverse operation"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(recalculate_prices, reverse_calc),
    ]
