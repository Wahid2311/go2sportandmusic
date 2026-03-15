from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from tickets.views import receive_bot_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('events.urls')),
    path('accounts/',include('accounts.urls')),
    # Add your bot API path directly to the master router:
    path('api/bot/receive-tickets/', receive_bot_data, name='receive_bot_data'),
    # path('tickets/',include('tickets.urls')),
]

# Serve static files in development 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
