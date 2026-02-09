from django.contrib import admin
from .models import Event, EventSection, ContactMessage
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_id', 'name', 'category_badge', 'date', 'time',
        'stadium_name', 'tickets_info', 'price_range', 'status_badge', 'created'
    )
    list_filter = ('date', 'created', 'superadmin')
    search_fields = ('event_id', 'name', 'stadium_name', 'superadmin__email')
    ordering = ('-date', '-time')
    readonly_fields = (
        'event_id', 'created', 'modified', 'total_tickets_display',
        'sold_tickets_display', 'left_tickets_display', 'time_left_display',
        'lowest_price_display', 'highest_price_display', 'is_expired_display',
        'total_sold_price_display'
    )
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Event Identification', {
            'fields': ('event_id', 'name', 'category_legacy', 'superadmin')
        }),
        ('Venue Information', {
            'fields': ('stadium_name', 'stadium_image', 'event_logo')
        }),
        ('Event Schedule', {
            'fields': ('date', 'time', 'time_left_display', 'is_expired_display')
        }),
        ('Service Charges', {
            'fields': ('normal_service_charge', 'reseller_service_charge'),
            'description': 'Service charges in percentage (%)'
        }),
        ('Ticket Information', {
            'fields': (
                'total_tickets_display', 'sold_tickets_display', 'left_tickets_display',
                'total_sold_price_display'
            ),
            'classes': ('collapse',)
        }),
        ('Price Range', {
            'fields': ('lowest_price_display', 'highest_price_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def category_badge(self, obj):
        color_map = {
            'concert': '#E6194B',
            'sports': '#3CB44B',
            'theater': '#4363D8',
            'conference': '#911EB4',
            'festival': '#F58231',
            'other': '#808080'
        }
        color = color_map.get(obj.category_legacy, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_category_legacy_display() if obj.category_legacy else 'N/A'
        )
    category_badge.short_description = 'Category'
    
    def tickets_info(self, obj):
        return f"{obj.sold_tickets}/{obj.total_tickets}"
    tickets_info.short_description = 'Tickets (Sold/Total)'
    
    def price_range(self, obj):
        return f"${obj.lowest_price:.2f} - ${obj.highest_price:.2f}"
    price_range.short_description = 'Price Range'
    
    def status_badge(self, obj):
        if obj.is_expired:
            color = '#999999'
            status = 'EXPIRED'
        elif obj.left_tickets == 0:
            color = '#E6194B'
            status = 'SOLD OUT'
        else:
            color = '#3CB44B'
            status = 'ACTIVE'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'
    
    def total_tickets_display(self, obj):
        return obj.total_tickets
    total_tickets_display.short_description = 'Total Tickets'
    
    def sold_tickets_display(self, obj):
        return obj.sold_tickets
    sold_tickets_display.short_description = 'Sold Tickets'
    
    def left_tickets_display(self, obj):
        return obj.left_tickets
    left_tickets_display.short_description = 'Tickets Left'
    
    def total_sold_price_display(self, obj):
        return f"${obj.total_sold_price:.2f}"
    total_sold_price_display.short_description = 'Total Sold Price'
    
    def time_left_display(self, obj):
        return obj.time_left
    time_left_display.short_description = 'Time Left'
    
    def lowest_price_display(self, obj):
        return f"${obj.lowest_price:.2f}"
    lowest_price_display.short_description = 'Lowest Price'
    
    def highest_price_display(self, obj):
        return f"${obj.highest_price:.2f}"
    highest_price_display.short_description = 'Highest Price'
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">✓ EXPIRED</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ ACTIVE</span>'
            )
    is_expired_display.short_description = 'Expiration Status'


@admin.register(EventSection)
class EventSectionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'event', 'color_display', 'price_range', 'created'
    )
    list_filter = ('event', 'created')
    search_fields = ('name', 'event__name', 'event__event_id')
    ordering = ('event', 'created')
    readonly_fields = ('created', 'modified', 'color_display')
    
    fieldsets = (
        ('Section Information', {
            'fields': ('event', 'name', 'color', 'color_display')
        }),
        ('Pricing', {
            'fields': ('lower_price', 'upper_price')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        # Find the color name from COLORS list
        color_name = None
        for hex_code, name in EventSection.COLORS:
            if hex_code == obj.color:
                color_name = name
                break
        
        return format_html(
            '<div style="background-color: {}; width: 50px; height: 50px; border-radius: 5px; border: 2px solid #ccc; display: inline-block;"></div> {} ({})',
            obj.color, color_name or 'Custom', obj.color
        )
    color_display.short_description = 'Color Preview'
    
    def price_range(self, obj):
        return f"${obj.lower_price:.2f} - ${obj.upper_price:.2f}"
    price_range.short_description = 'Price Range'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'name', 'email', 'phone', 'resolution_status', 'created_at'
    )
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'email', 'name', 'phone', 'subject', 'message')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Sender Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_resolved',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def resolution_status(self, obj):
        if obj.is_resolved:
            color = 'green'
            status = '✓ RESOLVED'
        else:
            color = 'orange'
            status = '⟳ PENDING'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, status
        )
    resolution_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        # Prevent adding contact messages from admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers
        return request.user.is_superuser