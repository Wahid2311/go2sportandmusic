from django.http import HttpResponsePermanentRedirect
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DomainRedirectMiddleware:
    """
    Middleware to redirect old domain to new domain.
    ONLY redirect go2sportandmusic.com to tickethouse.net
    DO NOT redirect tickethouse.net to itself
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the host header (could be from HTTP_HOST or X-Forwarded-Host)
        host = request.META.get('HTTP_HOST', '').lower()
        forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '').lower()
        
        # Use forwarded host if available (for proxies like Railway)
        if forwarded_host:
            host = forwarded_host
        
        logger.info(f"DomainRedirectMiddleware: host={host}, path={request.path}")
        
        # ONLY redirect if it's the OLD domain (go2sportandmusic.com)
        if 'go2sportandmusic' in host:
            logger.info(f"Redirecting {host} to tickethouse.net")
            return HttpResponsePermanentRedirect(f"https://tickethouse.net{request.path}")
        
        # For all other domains (including tickethouse.net), just serve normally
        response = self.get_response(request)
        return response
