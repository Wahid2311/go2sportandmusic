from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerificationToken
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'full_name', 'phone', 'user_type_badge', 'verification_status',
        'seller_status', 'is_staff', 'date_joined'
    )
    list_filter = (
        'user_type', 'is_verified', 'verified_seller', 'is_staff',
        'is_superadmin', 'is_active', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'full_name_display')
        }),
        ('Address', {
            'fields': ('country', 'city', 'street_no'),
            'classes': ('collapse',)
        }),
        ('Account Type', {
            'fields': ('user_type', 'verified_seller')
        }),
        ('Verification Status', {
            'fields': ('is_verified',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superadmin', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('social_media_link',),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('date_joined',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone', 'user_type', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('date_joined', 'full_name_display')
    filter_horizontal = ('groups', 'user_permissions')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "Not provided"
    full_name_display.short_description = 'Full Name Display'
    
    def user_type_badge(self, obj):
        color = 'blue' if obj.user_type == 'Reseller' else 'gray'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_user_type_display()
        )
    user_type_badge.short_description = 'User Type'
    
    def verification_status(self, obj):
        if obj.is_verified:
            color = 'green'
            status = '✓ Verified'
        else:
            color = 'red'
            status = '✗ Not Verified'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    verification_status.short_description = 'Verification'
    
    def seller_status(self, obj):
        if obj.verified_seller:
            color = 'green'
            status = '✓ Verified Seller'
        else:
            color = 'orange'
            status = '✗ Not Verified'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    seller_status.short_description = 'Seller Status'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'token_type_badge', 'is_used_status', 'token_short',
        'created_at', 'expires_at', 'is_valid_status'
    )
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'token_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token', 'token_display', 'token_type')
        }),
        ('Status', {
            'fields': ('is_used', 'is_valid_status_display')
        }),
        ('Dates', {
            'fields': ('created_at', 'expires_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        return str(obj.token)[:8] + '...'
    token_short.short_description = 'Token'
    
    def token_display(self, obj):
        return str(obj.token)
    token_display.short_description = 'Full Token'
    
    def token_type_badge(self, obj):
        color_map = {
            'signup': 'blue',
            'password_reset': 'orange',
            'superadmin': 'red'
        }
        color = color_map.get(obj.token_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_token_type_display()
        )
    token_type_badge.short_description = 'Token Type'
    
    def is_used_status(self, obj):
        if obj.is_used:
            color = 'red'
            status = '✓ Used'
        else:
            color = 'green'
            status = '✗ Unused'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    is_used_status.short_description = 'Usage Status'
    
    def is_valid_status(self, obj):
        return obj.is_valid()
    is_valid_status.boolean = True
    is_valid_status.short_description = 'Is Valid'
    
    def is_valid_status_display(self, obj):
        if obj.is_valid():
            color = 'green'
            status = '✓ Valid'
        else:
            color = 'red'
            status = '✗ Expired/Used'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    is_valid_status_display.short_description = 'Validity Status'