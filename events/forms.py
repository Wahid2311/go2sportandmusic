from django import forms
from django.utils import timezone
from .models import Event, ContactMessage, EventSection, EventCategory

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 234 567 890'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message here...',
                'rows': 5
            }),
        }

class EventCreationForm(forms.ModelForm):
    # Category field removed - using category_legacy instead
    
    class Meta:
        model = Event
        fields = [
            'name', 'category_legacy', 'sports_type', 'country', 'team',
            'stadium_name', 'stadium_image',
            'event_logo', 'date', 'time', 'normal_service_charge',
            'reseller_service_charge'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control event-form-input',
                'data-validation': 'event-name',
                'placeholder': 'Enter event name'
            }),
            'category_legacy': forms.Select(attrs={
                'class': 'form-control event-form-input'
            }),
            'sports_type': forms.TextInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'e.g. Football, Basketball (Optional)'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'Enter country'
            }),
            'team': forms.TextInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'Enter team name (Optional)'
            }),
            'stadium_name': forms.TextInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'Enter stadium name'
            }),
            'stadium_image': forms.URLInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'https://example.com/stadium-image.jpg'
            }),
            'event_logo': forms.URLInput(attrs={
                'class': 'form-control event-form-input',
                'placeholder': 'https://example.com/event-logo.png'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control event-form-date',
                'min': timezone.now().date().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control event-form-time'
            }),
            'normal_service_charge': forms.NumberInput(attrs={
                'class': 'form-control event-form-percentage',
                'step': '0.01',
                'data-behavior': 'service-charge',
                'data-user-type': 'normal'
            }),
            'reseller_service_charge': forms.NumberInput(attrs={
                'class': 'form-control event-form-percentage',
                'step': '0.01',
                'data-behavior': 'service-charge',
                'data-user-type': 'reseller'
            }),
        }

    sections = forms.JSONField(
        widget=forms.HiddenInput(),
        required=False,
        initial=list
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('date')
        event_time = cleaned_data.get('time')

        if event_date and event_date < timezone.now().date():
            self.add_error('date', 'Event date cannot be in the past')

        if event_date == timezone.now().date() and event_time:
            current_time = timezone.now().time()
            if event_time < current_time:
                self.add_error('time', 'Event time cannot be in the past for today')

        return cleaned_data

    def add_section(self, section_data):
        sections = self.cleaned_data.get('sections', [])
        sections.append({
            'name': section_data.get('name'),
            'color': section_data.get('color')
        })
        self.cleaned_data['sections'] = sections

class SectionForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control section-name',
            'placeholder': 'Section A',
            'data-validation': 'section-name'
        })
    )
    color = forms.ChoiceField(
        choices=EventSection.COLORS,
        widget=forms.Select(attrs={
            'class': 'form-control section-color'
        })
    )

class EventSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control search-input',
            'placeholder': 'Search events...',
            'data-behavior': 'search-autocomplete'
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control date-input',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control date-input',
            'type': 'date'
        })
    )

class EventFilterForm(forms.Form):
    SORT_CHOICES = [
        ('upcoming', 'Upcoming Events'),
        ('popular', 'Most Popular'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low')
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control filter-select',
            'data-behavior': 'sort-selector'
        })
    )
    category = forms.ChoiceField(
        choices=Event.EVENT_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control filter-select'
        })
    )