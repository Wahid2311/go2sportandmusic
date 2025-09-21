from django.urls import path
from . import views
from tickets import views as ticket_views

app_name = 'events'

urlpatterns = [
    path('superadmin/create-event/', views.EventCreateView.as_view(), name='event_create'),
    path('api/events/create/', views.EventCreateAPIView.as_view(), name='api_event_create'),
    path('api/events/update/<str:event_id>/', views.EventUpdateAPIView.as_view(), name='api_event_update'),
    path('api/events/all/', views.AllEventsAPIView.as_view(), name='api_events_all'),
    path('api/events/search/', views.EventSearchAPIView.as_view(), name='api_events_search'),
    path('api/events/expired/', views.ExpiredEventsAPIView.as_view(), name='api_events_expired'),
    path('api/events/delete/<str:event_id>/', views.EventDeleteAPIView.as_view(), name='api_event_delete'),
    path('superadmin/events/', views.SuperadminEventListView.as_view(), name='superadmin_event_list'),
    path('superadmin/events/<uuid:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('superadmin/expired-events/', views.ExpiredEventListView.as_view(), name='expired_events'),
    path('superadmin/events/<uuid:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    path('', views.HomeView.as_view(), name='home'),
    path('events/search-results/', views.EventSearchView.as_view(), name='search_results'),
    path('events/all/', views.AllEventsView.as_view(), name='all_events'),
    path('events/search-autocomplete/', views.SearchAutocompleteView.as_view(), name='search_autocomplete'),

    path('contact/', views.ContactView.as_view(), name='contact'),
     path('privacy-policy/', views.PrivacyView.as_view(), name='privacy'),

    path(
        'events/<str:event_id>/create-listing/',
        ticket_views.CreateListingView.as_view(),
        name='create_listing'
    ),

    path(
        'events/<str:event_id>/tickets/',
        ticket_views.EventTicketListView.as_view(),
        name='event_tickets'
    ),

    path(
        'my-listings/',
        ticket_views.MyListingsView.as_view(),
        name='my_listings'
    ),
    path(
        'tickets/<uuid:ticket_id>/update/',
        ticket_views.ResellerTicketUpdateView.as_view(),
        name='reseller_update'
    ),
    path(
        'tickets/<uuid:ticket_id>/delete/',
        ticket_views.ResellerTicketDeleteView.as_view(),
        name='reseller_delete'
    ),

    path(
        'superadmin/tickets/',
        ticket_views.SuperadminTicketListView.as_view(),
        name='superadmin_list'
    ),
    path(
        'superadmin/tickets/<uuid:ticket_id>/update/',
        ticket_views.SuperadminTicketUpdateView.as_view(),
        name='superadmin_update'
    ),
    path(
        'superadmin/tickets/<uuid:ticket_id>/delete/',
        ticket_views.SuperadminTicketDeleteView.as_view(),
        name='superadmin_delete'
    ),
    path(
        'superadmin/expired-tickets/',
        ticket_views.ExpiredTicketListView.as_view(),
        name='superadmin_expired'
    ),
    path(
        'superadmin/expired-tickets/<uuid:ticket_id>/notify/',
        ticket_views.ExpiredTicketNotifyView.as_view(),
        name='superadmin_notify'
    ),
    path(
        'get-section-prices/',
        ticket_views.SectionPriceAjaxView.as_view(),
        name='section_price_ajax'
    ),
    path(
        'get-event-prices/',
        views.NormalResellerPriceView.as_view(),
        name='event_price_ajax'
    ),
path(
    'events/<str:event_id>/tickets/<uuid:ticket_id>/',
    ticket_views.TicketDetailView.as_view(),
    name='ticket_detail'
),
path(
    'tickets/<uuid:ticket_id>/buy/',
    ticket_views.CreateOrderView.as_view(),
    name='create_order'
),
path(
    'payment/return/',
    ticket_views.PaymentReturnView.as_view(),
    name='payment_return'
),
path(
    'my-orders/',
    ticket_views.OrderListView.as_view(),
    name='my_orders'
),
path(
    'my-sales/',
    ticket_views.SaleListView.as_view(),
    name='my_sales'
),
path(
    'superadmin/orders/',
    ticket_views.SuperadminOrderListView.as_view(),
    name='superadmin_orders'
),
path(
    'superadmin/sales/',
    ticket_views.SuperadminSaleListView.as_view(),
    name='superadmin_sales'
),
path(
    'superadmin/orders/<uuid:order_id>/pay/',
    ticket_views.MarkAsPaidView.as_view(),
    name='mark_as_paid'
),
path('api/events/<str:event_id>/create-listing/',
         ticket_views.CreateListingAPIView.as_view(),
         name='api_create_listing'),

    path('api/tickets/update/<uuid:ticket_id>/',
         ticket_views.TicketUpdateAPIView.as_view(),
         name='api_ticket_update'),
    path('api/tickets/detail/<uuid:ticket_id>/',
         ticket_views.TicketDetailAPIView.as_view(),
         name='api_ticket_detail'),
    path('api/tickets/section-prices/',
         ticket_views.SectionPriceAPIView.as_view(),
         name='api_section_prices'),
    path('api/tickets/delete/<uuid:ticket_id>/',
         ticket_views.TicketDeleteAPIView.as_view(),
         name='api_ticket_delete'),
    path('api/tickets/my-listings/',
         ticket_views.MyListingsAPIView.as_view(),
         name='api_my_listings'),
path('api/events/<str:event_id>/tickets/',
         ticket_views.EventTicketListAPIView.as_view(),
         name='api_event_tickets'),
    path('api/events/<str:event_id>/sections/', 
         views.EventSectionsAPIView.as_view(), 
         name='api_event_sections'),
]

