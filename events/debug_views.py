from django.http import JsonResponse
from django.conf import settings
import stripe

def debug_stripe_key(request):
    """Debug endpoint to check Stripe key configuration"""
    # Allow access for debugging
    pass
    
    stripe_key = settings.STRIPE_SECRET_KEY
    
    return JsonResponse({
        'stripe_key_set': bool(stripe_key),
        'stripe_key_length': len(stripe_key) if stripe_key else 0,
        'stripe_key_start': stripe_key[:20] if stripe_key else 'NOT SET',
        'stripe_key_end': stripe_key[-10:] if stripe_key else 'NOT SET',
        'stripe_library_version': stripe.__version__,
        'base_url': settings.BASE_URL,
    })
