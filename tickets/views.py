import logging
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from .stripe_utils import StripeAPI
import stripe

logger = logging.getLogger(__name__)


@require_POST
@login_required
def create_checkout_session(request):
    """Create a Stripe checkout session for ticket purchase"""
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        quantity = int(data.get('quantity', 1))
        price = float(data.get('price', 0))
        description = data.get('description', 'Ticket Purchase')
        
        # Calculate total
        total_amount = price * quantity
        
        # Create Stripe checkout session
        stripe_api = StripeAPI()
        session_data = stripe_api.create_checkout_session(
            amount=total_amount,
            currency='gbp',
            customer_email=request.user.email,
            description=description,
            order_id=ticket_id
        )
        
        return JsonResponse({
            'session_id': session_data['session_id'],
            'checkout_url': session_data['checkout_url'],
        })
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@require_GET
def payment_return(request):
    """Handle Stripe payment return"""
    try:
        status = request.GET.get('status')
        session_id = request.GET.get('session_id')
        
        if status == 'success':
            return render(request, 'tickets/payment_success.html', {'session_id': session_id})
        elif status == 'cancelled':
            return render(request, 'tickets/payment_cancelled.html')
        else:
            return render(request, 'tickets/payment_failed.html')
    except Exception as e:
        logger.error(f"Error in payment return: {str(e)}")
        return render(request, 'tickets/payment_error.html', {'error': str(e)})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not hasattr(settings, 'STRIPE_WEBHOOK_SECRET'):
            return JsonResponse({'status': 'webhook_secret_not_configured'})
        
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            logger.info(f"Payment completed for session: {session['id']}")
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
