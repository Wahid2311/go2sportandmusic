"""
Middleware to ensure correct Stripe API key is used at runtime.
This bypasses environment variable caching issues.
"""
import os
import base64

class StripeKeyMiddleware:
    """Middleware to set Stripe API key on every request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Set the correct Stripe key immediately
        self._set_stripe_key()
    
    def __call__(self, request):
        # Ensure Stripe key is set correctly
        self._set_stripe_key()
        response = self.get_response(request)
        return response
    
    @staticmethod
    def _set_stripe_key():
        """Set the correct Stripe API key"""
        try:
            import stripe
            from django.conf import settings
            
            # Get the stripe key from settings (which may use the fallback from stripe_utils)
            stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            
            if stripe_key:
                stripe.api_key = stripe_key
        except Exception as e:
            # Log the error but don't crash
            print(f"Error setting Stripe key in middleware: {e}")
            pass
