from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.fields import ArrayField
from django.forms.widgets import CheckboxSelectMultiple
from datetime import timedelta

from .models import Ticket, BENEFITS_CHOICES, RESTRICTIONS_CHOICES, TICKET_TYPES
from events.models import Event, EventSection


class TicketForm(forms.ModelForm):
    upload_choice = forms.ChoiceField(
        choices=[('now', 'Upload Now'), ('later', 'Upload Later')],
        widget=forms.Select(attrs={
            'class': 'form-control ticket-input',
            'data-behavior': 'upload-choice'
        })
    )
    upload_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control ticket-input conditional-field',
            'data-conditional': 'upload-choice-now',
            'accept': 'application/pdf'
        })
    )
    upload_by = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control ticket-input conditional-field',
            'data-conditional': 'upload-choice-later'
        })
    )

    number_of_tickets = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ticket-input',
            'placeholder': 'Number of tickets',
            'data-validation': 'number'
        })
    )

    section = forms.ModelChoiceField(
        queryset=EventSection.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control ticket-input',
            'data-behavior': 'section-select'
        })
    )

    row = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control ticket-input',
            'placeholder': 'Row'
        })
    )

    seats = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control ticket-input',
            'placeholder': 'e.g. A1, A2, A3',
            'data-validation': 'seats'
        })
    )

    face_value = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ticket-input',
            'placeholder': 'Face value'
        })
    )

    ticket_type = forms.ChoiceField(
        choices=TICKET_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control ticket-input'
        })
    )

    benefits_and_Restrictions = forms.MultipleChoiceField(
        choices=RESTRICTIONS_CHOICES,
        required=False,
        widget=CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'data-behavior': 'restrictions-select'
        })
    )
    sell_price = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ticket-input',
            'placeholder': 'Your sell price',
            'data-behavior': 'price-input'
        })
    )

    class Meta:
        model = Ticket
        fields = [
            'upload_choice', 'upload_file', 'upload_by',
            'number_of_tickets', 'section', 'row', 'seats',
            'face_value', 'ticket_type', 'benefits_and_Restrictions', 'sell_price'
        ]

    def __init__(self, *args, **kwargs):
        
        event = kwargs.pop('event', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.seats:
            self.initial['seats'] = ', '.join(self.instance.seats)

        self.event = event

        if event:
            self.instance.event = event 
            self.fields['section'].queryset = EventSection.objects.filter(event=event)
            max_date = event.date - timedelta(days=1)
            self.fields['upload_by'].widget.attrs['max'] = max_date.isoformat()

        

    def clean_seats(self):
        seats_str = self.cleaned_data['seats']
        seats = [s.strip() for s in seats_str.split(',') if s.strip()]
        if len(seats) != self.cleaned_data.get('number_of_tickets', 0):
            raise ValidationError("Number of seats must equal number of tickets.")
        return seats

    def clean(self):
        cleaned = super().clean()
        upload_choice = cleaned.get('upload_choice')
        upload_file = cleaned.get('upload_file')
        upload_by = cleaned.get('upload_by')

        if upload_choice == 'now' and not upload_file:
            self.add_error('upload_file', "Please upload the PDF now.")
        if upload_choice == 'later':
            if not upload_by:
                self.add_error('upload_by', "Please select a date to upload before the event.")
            elif self.event and upload_by >= self.event.date:
                self.add_error('upload_by', "Upload date must be before the event date.")

        return cleaned

    def save(self, commit=True):
        self.instance.seats = self.cleaned_data['seats']
        if self.cleaned_data.get('upload_file'):
            self.instance.upload_file = self.cleaned_data['upload_file']
        return super().save(commit=commit)

