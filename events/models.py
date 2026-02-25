from django.db import models


class Category(models.Model):
    """Event category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """Event model"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Ticket model"""
    TICKET_TYPE_CHOICES = [
        ('e-ticket', 'E-Ticket'),
        ('paper', 'Paper'),
        ('mobile-transfer', 'Mobile Transfer'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    section = models.CharField(max_length=100)
    row = models.CharField(max_length=50, blank=True)
    seat_number = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='e-ticket')
    quantity_available = models.PositiveIntegerField(default=1)
    quantity_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['section', 'row', 'seat_number']
    
    def __str__(self):
        return f"{self.event.name} - {self.section}"
    
    @property
    def quantity_remaining(self):
        return self.quantity_available - self.quantity_sold
