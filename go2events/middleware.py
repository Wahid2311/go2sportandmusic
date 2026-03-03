from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class DomainRedirectMiddleware:
    """
    Middleware to redirect old domain to new domain.
    ONLY redirect go2sportandmusic.com to tickethouse.net
    DO NOT redirect tickethouse.net to itself
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the host header
        host = request.META.get('HTTP_HOST', '').lower()
        
        # ONLY redirect if it's the OLD domain
        if host.startswith('go2sportandmusic.com'):
            # Redirect to new domain
            return HttpResponsePermanentRedirect(f"https://tickethouse.net{request.path}")
        
        # For all other domains (including tickethouse.net), just serve normally
        response = self.get_response(request)
        return response
