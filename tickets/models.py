from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
import uuid
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class PdfStorage(S3Boto3Storage):
    location = 'tickets/pdfs'
    file_overwrite = False
    default_acl = 'private'

User = get_user_model()

TICKET_TYPES = [
    ('e-ticket', 'E-Ticket'),
    ('paper', 'Paper'),
    ('mobile-transfer', 'Mobile Transfer'),
]

BENEFITS_CHOICES = [
    ('vip_lounge', 'VIP Lounge'),
]

RESTRICTIONS_CHOICES = [
    ("select_features_disclosures", "Select features & disclosures"),
    ("restricted_view", "Restricted view (printed on ticket)"),
    ("child_16_under", "Child ticket (ages 16 and under)*"),
    ("child_18_under", "Child ticket (ages 18 and under)*"),
    ("junior_21_under", "Junior ticket (ages 21 and under)"),
    ("senior_61_older", "Senior ticket (61 and older)"),
    ("away_supporters_only", "Away Supporters Only"),
    ("home_supporters_only", "Home Supporters Only"),
    ("early_access", "Early Access"),
    ("vip_lounge_access", "Vip Lounge Access"),
    ("parking_pass", "Parking Pass"),
    ("full_suite_not_shared", "Full Suite (not shared)"),
    ("full_suite_shared", "Full Suite (Shared)"),
    ("unlimited_food_drinks", "Includes unlimited food and drinks"),
    ("limited_complimentary_food_drinks", "Includes limited complimentary food and drinks"),
    ("food_drink_voucher", "Food and drink voucher included"),
    ("food_drink_available_purchase", "Food and drink Available for Purchase"),
    ("pregame_food_beverage", "Includes pregame food and beverage"),
    ("free_halftime_drinks", "Free Halftime drinks"),
    ("complimentary_matchday_programme", "Complimentary matchday programme"),
    ("padded_seats", "Padded Seats"),
    ("standing_only", "Standing Only"),
    ("next_to_players_entrance", "Next to players' entrance"),
    ("validate", "Validate"),
]

class Ticket(models.Model):
    TICKET_TYPE_CHOICES = TICKET_TYPES
    id = models.AutoField(primary_key=True)
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='tickets')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_created')
    buyer = models.EmailField(null=True, blank=True)

    upload_choice = models.CharField(max_length=20, choices=[('now', 'Upload Now'), ('later', 'Upload Later')])
    upload_file = models.FileField(upload_to='',storage=PdfStorage(), null=True, blank=True)#
    upload_by = models.DateField(null=True, blank=True)

    number_of_tickets = models.PositiveIntegerField()
    section = models.ForeignKey('events.EventSection', on_delete=models.CASCADE, related_name='tickets')
    row = models.CharField(max_length=20)
    seats = ArrayField(models.CharField(max_length=10), help_text="Comma separated seat numbers.")
    face_value = models.DecimalField(max_digits=8, decimal_places=2)
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    benefits_and_Restrictions = ArrayField(models.CharField(max_length=50, choices=RESTRICTIONS_CHOICES), default=list, blank=True)

    
    sell_price = models.DecimalField(max_digits=8, decimal_places=2)
    sell_price_for_normal = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    sell_price_for_reseller = models.DecimalField(max_digits=8, decimal_places=2, editable=False)

    checked = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_id']),
            models.Index(fields=['event']),
            models.Index(fields=['seller']),
            models.Index(fields=['section']),
        ]

    def delete(self, *args, **kwargs):
        event = self.event
        section = self.section
        super().delete(*args, **kwargs)
        
        event.total_tickets = Ticket.objects.filter(event=event).aggregate(
            total=models.Sum('number_of_tickets')
        )['total'] or 0
        event.save()
        
        self.update_section_aggregates(section)

    def clean(self):
        if self.upload_choice == 'now' and not self.upload_file:
            raise ValidationError("PDF file must be uploaded if 'Upload Now' is selected.")
        if self.upload_choice == 'later' and not self.upload_by:
            raise ValidationError("Upload by date is required if 'Upload Later' is selected.")
        if self.upload_by and self.upload_by >= self.event.date:
            raise ValidationError("Upload date must be before the event date.")
        if len(self.seats) != self.number_of_tickets:
            raise ValidationError("Number of seats must match the number of tickets.")

    def save(self, *args, **kwargs):
        self.sell_price_for_normal = self.sell_price + (((self.sell_price*self.event.normal_service_charge)/100) or 0)
        self.sell_price_for_reseller = self.sell_price + (((self.sell_price*self.event.reseller_service_charge)/100) or 0)
        super().save(*args, **kwargs)

        section = self.section
        event = self.event
        all_tickets = section.tickets.all()
        
        if all_tickets.exists():
            prices = [float(t.sell_price) for t in all_tickets]
            section.lower_price = min(prices)
            section.upper_price = max(prices)
            section.save()
        event.total_tickets = sum(t.number_of_tickets for t in event.tickets.all())
        event.save()

        #self.update_event_section_aggregates()

    def update_section_aggregates(self, section):
        all_section_tickets = Ticket.objects.filter(section=section)
        all_prices = [ticket.sell_price for ticket in all_section_tickets]

        section.total_tickets = sum(ticket.number_of_tickets for ticket in all_section_tickets)
        section.lower_price = min(all_prices) if all_prices else 0
        section.upper_price = max(all_prices) if all_prices else 0
        section.save()

    def update_event_section_aggregates(self):
        section = self.section
        event = self.event
        all_section_tickets = section.tickets.all()
        
        if all_section_tickets.exists():
            all_prices = [float(ticket.sell_price) for ticket in all_section_tickets]
            section.lower_price = min(all_prices)
            section.upper_price = max(all_prices)
            section.total_tickets = sum(ticket.number_of_tickets for ticket in all_section_tickets)
        else:
            section.lower_price = 0
            section.upper_price = 0
            section.total_tickets = 0
        
        section.save()
        event.total_tickets = sum(t.number_of_tickets for t in event.tickets.all())
        event.save()

    @property
    def get_total_price(self):
        if self.seller.user_type=='Reseller':
            return self.number_of_tickets*self.sell_price_for_reseller
        return self.number_of_tickets*self.sell_price_for_normal

    def __str__(self):
        return f"{self.ticket_id} for {self.event.name}"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    number_of_tickets = models.PositiveIntegerField()
    ticket_reference = models.UUIDField(null=True, blank=True, editable=False)
    ticket_section = models.CharField(max_length=255)
    ticket_row = models.CharField(max_length=20)
    ticket_seats = ArrayField(models.CharField(max_length=10), help_text="Comma separated seat numbers.")
    ticket_face_value = models.DecimalField(max_digits=8, decimal_places=2)
    ticket_upload_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    ticket_benefits_and_Restrictions = ArrayField(models.CharField(max_length=50,default=list, blank=True))
    ticket_sell_price = models.DecimalField(max_digits=8, decimal_places=2)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    revolut_order_id = models.CharField(max_length=100)
    revolut_checkout_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    ticket_uploaded = models.BooleanField(default=False)
    paid_to_reseller = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} for {self.ticket}"

class Sale(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='sale')
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale for Order {self.order.id}"
