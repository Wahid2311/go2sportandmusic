"""Stripe payment processing utilities"""
import stripe
import logging
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class StripeAPI:
    """Stripe payment processing API"""
    
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured. Please set STRIPE_SECRET_KEY environment variable.")
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    @staticmethod
    def validate_config():
        """Validate that Stripe is properly configured"""
        if not settings.STRIPE_SECRET_KEY:
            return False, "Stripe secret key is not configured"
        if not settings.STRIPE_PUBLISHABLE_KEY:
            return False, "Stripe publishable key is not configured"
        return True, "Stripe is properly configured"
    
    def create_checkout_session(self, amount, currency, customer_email, description, order_id):
        """
        Create a Stripe checkout session for payment
        
        Args:
            amount: Amount in decimal (will be converted to cents)
            currency: Currency code (e.g., 'gbp')
            customer_email: Customer email address
            description: Payment description
            order_id: Order ID for reference
        
        Returns:
            Dictionary with session_id and checkout_url
        """
        try:
            success_url = settings.BASE_URL + reverse('events:payment_return') + '?status=success&session_id={CHECKOUT_SESSION_ID}&order_id=' + str(order_id)
            cancel_url = settings.BASE_URL + reverse('events:payment_return') + '?status=cancelled&order_id=' + str(order_id)
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': currency.lower(),
                            'unit_amount': int(amount * 100),  # Convert to cents
                            'product_data': {
                                'name': description,
                            },
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                customer_email=customer_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'order_id': str(order_id),
                }
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'payment_intent_id': session.payment_intent
            }
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {str(e)}")
            raise ValueError(f"Stripe authentication failed. Please check your API keys. Error: {str(e)}")
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Stripe invalid request error: {str(e)}")
            raise ValueError(f"Invalid Stripe request. Error: {str(e)}")
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise ValueError(f"Stripe payment processing failed. Error: {str(e)}")
    
    def retrieve_session(self, session_id):
        """
        Retrieve a Stripe checkout session
        """
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session: {str(e)}")
            raise ValueError(f"Failed to retrieve Stripe session. Error: {str(e)}")
    
    def retrieve_payment_intent(self, payment_intent_id):
        """
        Retrieve a Stripe payment intent
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            raise ValueError(f"Failed to retrieve Stripe payment intent. Error: {str(e)}")
    
    def is_configured(self):
        """Check if Stripe is properly configured"""
        return bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLISHABLE_KEY)
