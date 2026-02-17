# Generated migration to fix service charges and reseller purchase permissions

from django.db import migrations


def fix_service_charges(apps, schema_editor):
    """Set correct service charges: 20% for normal, 12% for reseller and recalculate ticket prices"""
    Event = apps.get_model('events', 'Event')
    
    # Update all events with correct service charges
    Event.objects.all().update(
        normal_service_charge=20,  # 20% for normal users
        reseller_service_charge=12  # 12% for resellers
    )
    
    print("✓ Updated service charges: Normal=20%, Reseller=12%")
    
    # Try to recalculate ticket prices, but only if the tickets table exists
    try:
        Ticket = apps.get_model('tickets', 'Ticket')
        for ticket in Ticket.objects.all():
            normal_charge = ticket.event.normal_service_charge or 0
            reseller_charge = ticket.event.reseller_service_charge or 0
            
            ticket.sell_price_for_normal = ticket.sell_price + (((ticket.sell_price * normal_charge) / 100) or 0)
            ticket.sell_price_for_reseller = ticket.sell_price + (((ticket.sell_price * reseller_charge) / 100) or 0)
            ticket.save(update_fields=['sell_price_for_normal', 'sell_price_for_reseller'])
        
        print(f"✓ Recalculated prices for {Ticket.objects.count()} tickets")
    except Exception as e:
        print(f"⚠ Could not recalculate ticket prices (table may not exist yet): {e}")


def reverse_fix(apps, schema_editor):
    """Reverse operation"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_reset_migration_history'),
    ]

    operations = [
        migrations.RunPython(fix_service_charges, reverse_fix),
    ]
