"""
Custom ID Generator for TicketHouse
Generates short, memorable, and professional-looking IDs
Examples: Order# 286884113, Ticket# 524891234
"""

import random
import string
from django.utils import timezone
from datetime import datetime


class CustomIDGenerator:
    """Generate short, memorable IDs for orders and tickets"""
    
    @staticmethod
    def generate_order_id():
        """
        Generate a formatted order ID like: ORD-286884113
        Format: ORD-{9 random digits}
        """
        random_part = ''.join(random.choices(string.digits, k=9))
        return f"ORD-{random_part}"
    
    @staticmethod
    def generate_ticket_id():
        """
        Generate a formatted ticket ID like: TKT-524891234
        Format: TKT-{9 random digits}
        """
        random_part = ''.join(random.choices(string.digits, k=9))
        return f"TKT-{random_part}"
    
    @staticmethod
    def generate_reference_id(prefix="REF"):
        """
        Generate a reference ID with prefix
        Format: REF-2026-03-04-XXXXX
        """
        now = timezone.now()
        date_str = now.strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=5))
        return f"{prefix}-{date_str}-{random_part}"
    
    @staticmethod
    def generate_short_code(length=8):
        """
        Generate a short alphanumeric code
        Format: ABC123XY
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))
