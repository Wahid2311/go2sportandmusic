from django.contrib import admin
from .models import Ticket, Order, Sale
from django.utils.html import format_html


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id_short', 'event', 'seller_email', 'number_of_tickets', 'section',
        'ticket_type', 'sell_price', 'status_badge', 'created_at'
    )
    list_filter = ('ticket_type', 'checked', 'ordered', 'sold', 'created_at', 'event', 'seller')
    search_fields = ('ticket_id', 'event__name', 'seller__email', 'section__name', 'buyer')
    ordering = ('-created_at',)
    readonly_fields = ('ticket_id', 'created_at', 'sell_price_for_normal', 'sell_price_for_reseller')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Ticket Identification', {
            'fields': ('ticket_id', 'event', 'seller', 'buyer')
        }),
        ('Upload Details', {
            'fields': ('upload_choice', 'upload_file', 'upload_by')
        }),
        ('Ticket Details', {
            'fields': ('number_of_tickets', 'section', 'row', 'seats')
        }),
        ('Pricing', {
            'fields': ('face_value', 'sell_price', 'sell_price_for_normal', 'sell_price_for_reseller'),
            'classes': ('collapse',)
        }),
        ('Ticket Type & Benefits', {
            'fields': ('ticket_type', 'benefits_and_Restrictions')
        }),
        ('Status', {
            'fields': ('checked', 'ordered', 'sold')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def ticket_id_short(self, obj):
        return str(obj.ticket_id)[:8] + '...'
    ticket_id_short.short_description = 'Ticket ID'
    
    def seller_email(self, obj):
        return obj.seller.email
    seller_email.short_description = 'Seller'
    
    def status_badge(self, obj):
        if obj.sold:
            color = 'green'
            status = 'SOLD'
        elif obj.ordered:
            color = 'orange'
            status = 'ORDERED'
        elif obj.checked:
            color = 'blue'
            status = 'CHECKED'
        else:
            color = 'gray'
            status = 'DRAFT'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id_short', 'event_name', 'event_date', 'buyer_email', 'number_of_tickets',
        'amount', 'status_badge', 'ticket_uploaded', 'paid_to_reseller', 'created_at'
    )
    list_filter = ('status', 'ticket_uploaded', 'paid_to_reseller', 'event_date', 'created_at')
    search_fields = ('id', 'event_name', 'buyer__email', 'ticket_reference', 'revolut_order_id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'revolut_order_id')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'buyer', 'status', 'created_at')
        }),
        ('Event Details', {
            'fields': ('event_name', 'event_date', 'event_time')
        }),
        ('Ticket Details', {
            'fields': ('ticket_reference', 'number_of_tickets', 'ticket_section', 'ticket_row', 'ticket_seats')
        }),
        ('Ticket Information', {
            'fields': ('ticket_face_value', 'ticket_upload_type', 'ticket_benefits_and_Restrictions', 'ticket_sell_price'),
            'classes': ('collapse',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'revolut_order_id', 'revolut_checkout_url'),
            'classes': ('collapse',)
        }),
        ('Fulfillment', {
            'fields': ('ticket_uploaded', 'paid_to_reseller')
        }),
    )
    
    def order_id_short(self, obj):
        return str(obj.id)[:8] + '...'
    order_id_short.short_description = 'Order ID'
    
    def buyer_email(self, obj):
        return obj.buyer.email
    buyer_email.short_description = 'Buyer'
    
    def status_badge(self, obj):
        color_map = {
            'completed': 'green',
            'pending': 'orange',
            'failed': 'red'
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; text-transform: uppercase;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'sale_id_short', 'order_short', 'seller_email', 'amount',
        'payout_status', 'created_at'
    )
    list_filter = ('payout_date', 'created_at', 'seller')
    search_fields = ('order__id', 'seller__email', 'order__event_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('order', 'seller')
        }),
        ('Amount Details', {
            'fields': ('amount',)
        }),
        ('Payout Information', {
            'fields': ('payout_date',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def sale_id_short(self, obj):
        return f'Sale-{obj.id}'[:8] + '...'
    sale_id_short.short_description = 'Sale ID'
    
    def order_short(self, obj):
        return str(obj.order.id)[:8] + '...'
    order_short.short_description = 'Order'
    
    def seller_email(self, obj):
        return obj.seller.email
    seller_email.short_description = 'Seller'
    
    def payout_status(self, obj):
        if obj.payout_date:
            color = 'green'
            status = f'PAID - {obj.payout_date}'
        else:
            color = 'orange'
            status = 'PENDING'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    payout_status.short_description = 'Payout Status'