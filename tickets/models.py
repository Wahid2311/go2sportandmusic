from django.db import models
from django.contrib.auth import get_user_model
from events.models import Ticket

User = get_user_model()


class Order(models.Model):
    """Model for ticket orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='gbp')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.email} - {self.status}"


class Sale(models.Model):
    """Model for individual ticket sales"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sales')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale {self.id} - {self.ticket} - {self.quantity} tickets"
