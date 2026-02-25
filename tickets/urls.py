from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-return/', views.payment_return, name='payment_return'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
