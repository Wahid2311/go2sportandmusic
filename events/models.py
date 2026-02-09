import uuid
import random
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import Sum, Min, Max

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class EventCategory(models.Model):
    """Dynamic event categories fetched from xs2events portal"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For Bootstrap icon classes
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name


class Event(BaseModel):
    EVENT_CATEGORIES = [
        ('concert', 'Concert'),
        ('sports', 'Sports'),
        ('theater', 'Theater'),
        ('conference', 'Conference'),
        ('festival', 'Festival'),
        ('other', 'Other'),
    ]
    
    STADIUM_SVG_CHOICES = [
        ('emiratesStadium', 'Emirates Stadium'),
        ('villaParkStadium', 'Villa Park Stadium'),
        ('oldTraffordStadium', 'Old Trafford'),
        ('anfieldStadium', 'Anfield Stadium'),
        ('ellandStadium', 'Elland Road'),
        ('tottenhamHotspurStadium', 'Tottenham Hotspur Stadium'),
        ('hillDickinsonStadium', 'Hill Dickinson Stadium'),
        ('sanSiro', 'San Siro'),
        ('molineux', 'Molineux Stadium'),
        ('cravenCottage', 'Craven Cottage'),
        ('etihadStadium', 'Etihad Stadium'),
        ('santiagoBernabeuStadium', 'Santiago Bernabéu Stadium'),
        ('riyadhMetropolitanoStadium', 'Riyadh Metropolitano Stadium'),
        ('gtechCommunityStadium', 'Gtech Community Stadium'),
        ('stamfordBridge', 'Stamford Bridge'),
        ('turfMoorStadium', 'Turf Moor Stadium'),
        ('queenElizabethOlympicPark', 'Queen Elizabeth Olympic Park'),
        ('selhurstPark', 'Selhurst Park'),
        ('celticStadium', 'Celtic Stadium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=6, unique=True, editable=False)
    superadmin = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    name = models.CharField(max_length=255, validators=[
        RegexValidator(r'^[a-zA-Z0-9\s\-\.]+$', 'Only letters, numbers, spaces, hyphens and periods allowed')
    ])
    category_legacy = models.CharField(max_length=20, choices=EVENT_CATEGORIES, null=True, blank=True)  # For backward compatibility
    sports_type = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    team = models.CharField(max_length=100, blank=True, null=True)
    stadium_name = models.CharField(max_length=255)
    stadium_image = models.URLField(max_length=500)
    event_logo = models.URLField(max_length=500)
    stadium_svg_key = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        choices=STADIUM_SVG_CHOICES,
        help_text="SVG key for interactive stadium map. Leave blank if no SVG available."
    )
    
    date = models.DateField()
    time = models.TimeField()
    
    normal_service_charge = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Service charge for normal users (no maximum limit)"
    )
    reseller_service_charge = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Service charge for resellers (no maximum limit)"
    )
    
    total_tickets = models.PositiveIntegerField(default=0)
    sold_tickets = models.PositiveIntegerField(default=0)
    total_sold_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['date', 'time']),
            models.Index(fields=['category']),
        ]
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.name} ({self.event_id})"

    def save(self, *args, **kwargs):
        if not self.event_id:
            self.event_id = self.generate_unique_event_id()
        super().save(*args, **kwargs)

    def generate_unique_event_id(self):
        while True:
            event_id = str(random.randint(100000, 999999))
            if not Event.objects.filter(event_id=event_id).exists():
                return event_id

    @property
    def time_left(self):
        now = timezone.now()
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        delta = event_datetime - now
        
        months = delta.days // 30
        days = delta.days % 30
        hours = delta.seconds // 3600
        
        return f"{months} months {days} days {hours} hours left"

    @property
    def event_timestamp(self):
        """Returns Unix timestamp of event datetime for JavaScript countdown timers"""
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return int(event_datetime.timestamp())

    @property
    def left_tickets(self):
        return self.total_tickets - self.sold_tickets

    @property
    def lowest_price(self):
        return self.sections.exclude(lower_price=0).exclude(lower_price__isnull=True).aggregate(Min('lower_price'))['lower_price__min'] or 0
    
    @property
    def highest_price(self):
        return self.sections.exclude(upper_price=0).exclude(upper_price__isnull=True).aggregate(Max('upper_price'))['upper_price__max'] or 0


    @property
    def is_expired(self):
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return event_datetime < timezone.now()

    @property
    def has_interactive_map(self):
        """Check if this event has an interactive SVG stadium map available"""
        return self.stadium_svg_key is not None and self.stadium_svg_key != ''
    
    def get_category_display(self):
        """Get category display name from dynamic or legacy category"""
        if self.category:
            return self.category.name
        elif self.category_legacy:
            return dict(self.EVENT_CATEGORIES).get(self.category_legacy, self.category_legacy)
        return 'Other'

class EventSection(BaseModel):
    COLORS = [
        ('#E6194B', 'Red'),
        ('#3CB44B', 'Green'),
        ('#4363D8', 'Blue'),
        ('#911EB4', 'Purple'),
        ('#F58231', 'Orange'),
        ('#46F0F0', 'Cyan'),
        ('#F032E6', 'Magenta'),
        ('#FABED4', 'Pink'),
        ('#FFE119', 'Yellow'),
        ('#808080', 'Gray'),
        ('#48869E', 'Steel Blue'),
        ('#205269', 'Dark Slate Blue'),
        ('#D18D6D', 'Tan'),
        ('#5A5833', 'Olive Drab'),
        ('#8F1D60', 'Dark Magenta'),
        ('#7FD469', 'Light Green'),
        ('#BAD151', 'Yellow Green'),
        ('#5663AD', 'Slate Blue'),
        ('#AA7EB3', 'Orchid'),
        ('#19B421', 'Green'),
        ('#9E4877', 'Medium Violet Red'),
        ('#1B507C', 'Dark Blue'),
        ('#AAA42C', 'Olive'),
        ('#495216', 'Dark Olive Green'),
        ('#24888B', 'Teal'),
        ('#46AA18', 'Lime Green'),
        ('#384B9E', 'Royal Blue'),
        ('#2AA4A8', 'Cadet Blue'),
        ('#165711', 'Forest Green'),
        ('#FFFFFF', 'White'),
        ('#25A73B', 'Lime'),
        ('#C4D434', 'Yellow Green'),
        ('#7A3164', 'Medium Violet Red'),
        ('#E6E06E', 'Khaki'),
        ('#698BD4', 'Cornflower Blue'),
        ('#606E1D', 'Olive Green'),
        ('#AD5673', 'Pale Violet Red'),
        ('#1B7C23', 'Dark Green'),
        ('#62A7D4', 'Sky Blue'),
        ('#972D6B', 'Purple'),
        ('#AFA521', 'Dark Khaki'),
        ('#EEC615', 'Gold'),
        ('#238028', 'Sea Green'),
        ('#CEAC17', 'Goldenrod'),
        ('#7C1B6C', 'Dark Orchid'),
        ('#A34B22', 'Sienna'),
        ('#2C71AA', 'Steel Blue'),
        ('#8A8418', 'Olive'),
        ('#8F2A68', 'Dark Magenta'),
        ('#C7A81F', 'Goldenrod'),
        ('#219AAF', 'Light Sea Green'),
        ('#3ABB41', 'Medium Sea Green'),
        ('#33A32F', 'Green'),
        ('#EBA817', 'Orange'),
        ('#BB3AAA', 'Medium Orchid'),
        ('#B63818', 'Firebrick'),
        ('#2E839C', 'Cadet Blue'),
        ('#A12D33', 'Brown'),
        ('#D21EFF', 'Magenta'),
        ('#B0B930', 'Olive Drab'),
        ('#3287CD', 'Dodger Blue'),
        ('#D18718', 'Dark Goldenrod'),
        ('#CF2A4E', 'Crimson'),
        ('#22791A', 'Forest Green'),
        ('#8D2D32', 'Dark Red'),
        ('#2B80E2', 'Dodger Blue'),
        ('#33A16E', 'Medium Sea Green'),
        ('#8D1B1B', 'Maroon'),
        ('#1A8817', 'Green'),
        ('#A8551D', 'Peru'),
        ('#9E1B7D', 'Purple'),
        ('#AD371A', 'Brown'),
        ('#5080C7', 'Cornflower Blue'),
        ('#707219', 'Olive Drab'),
        ('#BB1655', 'Deep Pink'),
        ('#68172B', 'Dark Red'),
        ('#7A2B76', 'Dark Orchid'),
        ('#CE5829', 'Chocolate'),
        ('#FFFFFE', 'White'),
        ('#A58D21', 'Olive'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, validators=[
        RegexValidator(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', 'Enter a valid hex color code')
    ])
    lower_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    upper_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        unique_together = ('event', 'name')
        ordering = ['created']

    def __str__(self):
        return f"{self.name} ({self.event.name})"

    def update_prices(self, lower, upper):
        self.lower_price = lower
        self.upper_price = upper
        self.save(update_fields=['lower_price', 'upper_price', 'modified'])

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"


class Category(models.Model):
    TYPE_CHOICES = [
        ('team', 'Team'),
        ('tournament', 'Tournament'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'type', 'country')
    # parent = models.ForeignKey(
    #     "self",
    #     # null : True,
    #     # blank : True ,
    #     # related_name 
    # )