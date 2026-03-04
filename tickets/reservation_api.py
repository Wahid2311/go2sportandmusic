"""
API endpoints for ticket reservation management.
"""
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Ticket, TicketReservation, Order
from .reservation_utils import (
    create_ticket_reservation,
    get_available_tickets,
    get_reservation_time_remaining,
    release_expired_reservations
)
import logging

logger = logging.getLogger(__name__)


class ReservationStatusView(LoginRequiredMixin, View):
    """
    Get the status of a reservation including time remaining.
    """
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            # Check if order has a reservation
            if hasattr(order, 'reservation'):
                reservation = order.reservation
                
                if reservation.is_expired:
                    return JsonResponse({
                        'status': 'expired',
                        'time_remaining': 0,
                        'message': 'Reservation has expired. Tickets are now available again.'
                    })
                else:
                    time_remaining = get_reservation_time_remaining(reservation)
                    return JsonResponse({
                        'status': 'active',
                        'time_remaining': time_remaining,
                        'expires_at': reservation.expires_at.isoformat(),
                        'quantity_reserved': reservation.quantity_reserved
                    })
            else:
                return JsonResponse({
                    'status': 'no_reservation',
                    'message': 'No active reservation for this order'
                }, status=404)
                
        except Exception as e:
            logger.error(f"Error getting reservation status: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class AvailableTicketsView(LoginRequiredMixin, View):
    """
    Get the number of available tickets for a given ticket listing.
    This accounts for active reservations.
    """
    def get(self, request, ticket_id):
        try:
            ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
            available = get_available_tickets(ticket)
            
            return JsonResponse({
                'ticket_id': str(ticket.ticket_id),
                'total_tickets': ticket.number_of_tickets,
                'available_tickets': available,
                'reserved_tickets': ticket.number_of_tickets - available
            })
            
        except Exception as e:
            logger.error(f"Error getting available tickets: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class ReleaseExpiredReservationsView(View):
    """
    Admin endpoint to manually trigger release of expired reservations.
    This should be called periodically by a background task.
    """
    def post(self, request):
        try:
            # In production, this should be protected by API key or admin check
            count = release_expired_reservations()
            return JsonResponse({
                'status': 'success',
                'released_count': count
            })
        except Exception as e:
            logger.error(f"Error releasing expired reservations: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class CheckReservationExpiryView(LoginRequiredMixin, View):
    """
    Check if a reservation has expired and return current status.
    Used by the checkout page to monitor reservation timer.
    """
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id, buyer=request.user)
            
            if not hasattr(order, 'reservation'):
                return JsonResponse({
                    'expired': False,
                    'message': 'No reservation found'
                })
            
            reservation = order.reservation
            
            # Check if expired
            if reservation.is_expired or reservation.get_time_remaining() <= 0:
                reservation.is_expired = True
                reservation.save()
                return JsonResponse({
                    'expired': True,
                    'time_remaining': 0,
                    'message': 'Your reservation has expired. Tickets are now available for other customers.'
                })
            else:
                time_remaining = reservation.get_time_remaining()
                return JsonResponse({
                    'expired': False,
                    'time_remaining': time_remaining,
                    'expires_at': reservation.expires_at.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error checking reservation expiry: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
