"""
Utility functions for managing ticket reservations with 10-minute expiration.
"""
from django.utils import timezone
from datetime import timedelta
from .models import TicketReservation, Ticket
import logging

logger = logging.getLogger(__name__)


def create_ticket_reservation(ticket, buyer, quantity):
    """
    Create a reservation for a ticket during checkout.
    The ticket is reserved for 10 minutes.
    
    Args:
        ticket: Ticket instance to reserve
        buyer: User instance (buyer)
        quantity: Number of tickets to reserve
        
    Returns:
        TicketReservation instance
    """
    reservation = TicketReservation.objects.create(
        ticket=ticket,
        buyer=buyer,
        quantity_reserved=quantity,
        expires_at=timezone.now() + timedelta(minutes=10)
    )
    logger.info(f"Created reservation {reservation.id} for ticket {ticket.ticket_id} by {buyer.email}")
    return reservation


def release_expired_reservations():
    """
    Find and mark all expired reservations as expired.
    This should be called periodically by a background task.
    
    Returns:
        Number of reservations released
    """
    now = timezone.now()
    expired_reservations = TicketReservation.objects.filter(
        expires_at__lte=now,
        is_expired=False
    )
    
    count = expired_reservations.count()
    expired_reservations.update(is_expired=True)
    
    logger.info(f"Released {count} expired ticket reservations")
    return count


def get_available_tickets(ticket):
    """
    Calculate the number of available tickets for a given ticket listing.
    This accounts for active reservations.
    
    Args:
        ticket: Ticket instance
        
    Returns:
        Number of available tickets (accounting for reservations)
    """
    # Get all active (non-expired) reservations for this ticket
    active_reservations = TicketReservation.objects.filter(
        ticket=ticket,
        is_expired=False,
        expires_at__gt=timezone.now()
    )
    
    reserved_quantity = sum(
        res.quantity_reserved for res in active_reservations
    )
    
    available = ticket.number_of_tickets - reserved_quantity
    return max(0, available)


def confirm_reservation(reservation):
    """
    Confirm a reservation after successful payment.
    This converts the reservation into a sold ticket.
    
    Args:
        reservation: TicketReservation instance
        
    Returns:
        Boolean indicating success
    """
    try:
        ticket = reservation.ticket
        
        # Mark the ticket as sold
        ticket.sold = True
        ticket.buyer = reservation.buyer.email
        ticket.save()
        
        logger.info(f"Confirmed reservation {reservation.id} - ticket {ticket.ticket_id} marked as sold")
        return True
    except Exception as e:
        logger.error(f"Error confirming reservation {reservation.id}: {str(e)}")
        return False


def cancel_reservation(reservation):
    """
    Cancel a reservation (e.g., if payment fails or customer cancels).
    This releases the reserved tickets back to the pool.
    
    Args:
        reservation: TicketReservation instance
        
    Returns:
        Boolean indicating success
    """
    try:
        reservation.is_expired = True
        reservation.save()
        
        logger.info(f"Cancelled reservation {reservation.id} for ticket {reservation.ticket.ticket_id}")
        return True
    except Exception as e:
        logger.error(f"Error cancelling reservation {reservation.id}: {str(e)}")
        return False


def get_reservation_time_remaining(reservation):
    """
    Get the remaining time for a reservation in seconds.
    
    Args:
        reservation: TicketReservation instance
        
    Returns:
        Number of seconds remaining (0 if expired)
    """
    if reservation.is_expired:
        return 0
    
    remaining = reservation.expires_at - timezone.now()
    return max(0, int(remaining.total_seconds()))
