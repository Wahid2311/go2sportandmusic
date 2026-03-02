from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class DomainRedirectMiddleware(MiddlewareMixin):
    """Middleware to redirect old domain to new domain and HTTP to HTTPS"""
    
    def process_request(self, request):
        # Get the host from the request
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Redirect old domain to new domain ONLY
        if host == 'go2sportandmusic.com' or host == 'www.go2sportandmusic.com':
            # Build the new URL with the new domain
            new_url = request.build_absolute_uri(request.get_full_path())
            new_url = new_url.replace('go2sportandmusic.com', 'tickethouse.net')
            new_url = new_url.replace('www.go2sportandmusic.com', 'tickethouse.net')
            # Ensure HTTPS
            if not new_url.startswith('https://'):
                new_url = new_url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(new_url)
        
        # For tickethouse.net, only redirect HTTP to HTTPS
        if host == 'tickethouse.net' and not request.is_secure():
            new_url = request.build_absolute_uri(request.get_full_path())
            new_url = new_url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(new_url)
        
        return None
