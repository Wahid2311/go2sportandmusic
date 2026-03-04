from django import template
import hashlib

register = template.Library()

@register.filter
def ticket_display_id(ticket_obj):
    """
    Display ticket ID in custom format.
    If ticket_number exists, use it. Otherwise generate from ticket_id UUID.
    Format: Ticket# XXXXXXXXX (9 digits)
    """
    if hasattr(ticket_obj, 'ticket_number') and ticket_obj.ticket_number:
        return f"Ticket# {ticket_obj.ticket_number}"
    
    if hasattr(ticket_obj, 'ticket_id'):
        # Generate a consistent 9-digit number from the UUID
        uuid_str = str(ticket_obj.ticket_id)
        hash_obj = hashlib.md5(uuid_str.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        ticket_num = str(hash_int % 1000000000).zfill(9)
        return f"Ticket# {ticket_num}"
    
    return "Ticket# Unknown"

@register.filter
def order_display_id(order_obj):
    """
    Display order ID in custom format.
    If order_number exists, use it. Otherwise generate from order id UUID.
    Format: Order# XXXXXXXXX (9 digits)
    """
    if hasattr(order_obj, 'order_number') and order_obj.order_number:
        return f"Order# {order_obj.order_number}"
    
    if hasattr(order_obj, 'id'):
        # Generate a consistent 9-digit number from the UUID
        uuid_str = str(order_obj.id)
        hash_obj = hashlib.md5(uuid_str.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        order_num = str(hash_int % 1000000000).zfill(9)
        return f"Order# {order_num}"
    
    return "Order# Unknown"
