from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class DomainRedirectMiddleware(MiddlewareMixin):
      """Redirect old domain to new domain and enforce HTTPS."""

    def process_request(self, request):
              host = request.get_host().lower()

        # Remove port from host if present
              if ':' in host:
                            host = host.split(':')[0]

              # Redirect go2sportandmusic.com to tickethouse.net
              if host == 'go2sportandmusic.com':
                            protocol = 'https' if request.is_secure() else 'https'
                            new_url = f'{protocol}://tickethouse.net{request.get_full_path()}'
                            return HttpResponsePermanentRedirect(new_url)

              # Enforce HTTPS for all domains
              if not request.is_secure() and request.method == 'GET':
                            protocol = 'https'
                            new_url = f'{protocol}://{host}{request.get_full_path()}'
                            return HttpResponsePermanentRedirect(new_url)

              return None
      
