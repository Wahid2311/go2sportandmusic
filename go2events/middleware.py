from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class DomainRedirectMiddleware(MiddlewareMixin):
    """Middleware to redirect old domain to new domain and HTTP to HTTPS"""
    
    def process_request(self, request):
        # Get the host from the request
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # ONLY redirect old domain to new domain
        if host.lower() in ['go2sportandmusic.com', 'www.go2sportandmusic.com']:
            # Build the new URL with the new domain
            new_url = request.build_absolute_uri(request.get_full_path())
            new_url = new_url.replace('go2sportandmusic.com', 'tickethouse.net')
            new_url = new_url.replace('www.go2sportandmusic.com', 'tickethouse.net')
            # Ensure HTTPS
            if not new_url.startswith('https://'):
                new_url = new_url.replace('http://', 'https://')
            logger.info(f"Redirecting {host} to {new_url}")
            return HttpResponsePermanentRedirect(new_url)
        
        # For tickethouse.net, only redirect HTTP to HTTPS
        if host.lower() == 'tickethouse.net' and not request.is_secure():
            new_url = request.build_absolute_uri(request.get_full_path())
            new_url = new_url.replace('http://', 'https://')
            logger.info(f"Redirecting HTTP to HTTPS for {host}")
            return HttpResponsePermanentRedirect(new_url)
        
        # For all other hosts (including tickethouse.net HTTPS), don't redirect
        return None
