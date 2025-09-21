from django.urls import path,include

urlpatterns = [
    path('',include('events.urls')),
    path('accounts/',include('accounts.urls')),
]
