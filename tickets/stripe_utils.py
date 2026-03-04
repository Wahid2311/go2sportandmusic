"""Stripe payment processing utilities"""
import stripe
import logging
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def initialize_stripe():
    """Initialize Stripe with API key from settings"""
    if not settings.STRIPE_SECRET_KEY:
        logger.error("STRIPE_SECRET_KEY is not configured in settings")
        raise ValueError("STRIPE_SECRET_KEY is not configured")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.info(f"Stripe initialized with key ending in: {settings.STRIPE_SECRET_KEY[-10:]}")


class StripeAPI:
    """Stripe payment processing API"""
    
    def __init__(self):
        """Initialize Stripe API with secret key"""
        initialize_stripe()
    
    def create_checkout_session(self, amount, currency, customer_email, description, order_id, request=None):
        """
        Create a Stripe checkout session for payment
        
        Args:
            amount: Amount in decimal (will be converted to cents)
            currency: Currency code (e.g., 'gbp')
            customer_email: Customer email address
            description: Payment description
            order_id: Order ID for reference
            request: Django request object (optional, for getting correct domain)
        
        Returns:
            Dictionary with session_id and checkout_url
        """
        try:
            # Build success and cancel URLs using request's domain if available
            if request:
                base_url = request.build_absolute_uri('/').rstrip('/')
            else:
                base_url = settings.BASE_URL
            
            # Note: Stripe will replace {CHECKOUT_SESSION_ID} with the actual session ID
            success_url = base_url + reverse('events:payment_return') + '?status=success&session_id={CHECKOUT_SESSION_ID}&order_id=' + str(order_id)
            cancel_url = base_url + reverse('events:payment_return') + '?status=cancelled&order_id=' + str(order_id)
            
            logger.info(f"Creating Stripe checkout session for order {order_id}, amount: {amount} {currency}")
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card', 'link'],
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
            
            logger.info(f"Stripe checkout session created: {session.id}")
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'payment_intent_id': session.payment_intent
            }
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {str(e)}")
            logger.error(f"API key being used ends with: {stripe.api_key[-10:] if stripe.api_key else 'NOT SET'}")
            raise
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating checkout session: {str(e)}")
            raise
    
    def retrieve_session(self, session_id):
        """
        Retrieve a Stripe checkout session
        """
        try:
            logger.info(f"Retrieving Stripe session: {session_id}")
            session = stripe.checkout.Session.retrieve(session_id)
            logger.info(f"Session retrieved, payment status: {session.payment_status}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving session: {str(e)}")
            raise
    
    def retrieve_payment_intent(self, payment_intent_id):
        """
        Retrieve a Stripe payment intent
        """
        try:
            logger.info(f"Retrieving Stripe payment intent: {payment_intent_id}")
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.info(f"Payment intent retrieved, status: {intent.status}")
            return intent
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving payment intent: {str(e)}")
            raise
