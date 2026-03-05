from django.db import migrations
from tickets.id_generator import CustomIDGenerator

def populate_ticket_numbers(apps, schema_editor):
    """Populate ticket_number for all existing tickets using raw SQL to avoid JSON parsing issues"""
    from django.db import connection
    with connection.cursor() as cursor:
        # Use raw SQL to update tickets with null ticket_number
        # This avoids Django trying to deserialize potentially malformed JSON fields
        try:
            cursor.execute("""
                UPDATE tickets_ticket 
                SET ticket_number = %s 
                WHERE ticket_number IS NULL 
                LIMIT 1
            """, [CustomIDGenerator.generate_ticket_id()])
            
            # Keep updating until no more tickets need updating
            while cursor.rowcount > 0:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET ticket_number = %s 
                    WHERE ticket_number IS NULL 
                    LIMIT 1
                """, [CustomIDGenerator.generate_ticket_id()])
        except Exception as e:
            # If there's any error, just continue - the IDs will be generated on-demand
            print(f"Warning: Could not populate ticket numbers: {e}")

def populate_order_numbers(apps, schema_editor):
    """Populate order_number for all existing orders using raw SQL"""
    from django.db import connection
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                UPDATE tickets_order 
                SET order_number = %s 
                WHERE order_number IS NULL 
                LIMIT 1
            """, [CustomIDGenerator.generate_order_id()])
            
            # Keep updating until no more orders need updating
            while cursor.rowcount > 0:
                cursor.execute("""
                    UPDATE tickets_order 
                    SET order_number = %s 
                    WHERE order_number IS NULL 
                    LIMIT 1
                """, [CustomIDGenerator.generate_order_id()])
        except Exception as e:
            # If there's any error, just continue - the IDs will be generated on-demand
            print(f"Warning: Could not populate order numbers: {e}")

def reverse_populate(apps, schema_editor):
    """Reverse migration - clear the custom IDs"""
    from django.db import connection
    with connection.cursor() as cursor:
        try:
            cursor.execute("UPDATE tickets_ticket SET ticket_number = NULL")
            cursor.execute("UPDATE tickets_order SET order_number = NULL")
        except Exception as e:
            print(f"Warning: Could not reverse populate: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_add_custom_ids'),
    ]

    operations = [
        migrations.RunPython(populate_ticket_numbers, reverse_populate),
        migrations.RunPython(populate_order_numbers, reverse_populate),
    ]
