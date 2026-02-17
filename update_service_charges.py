#!/usr/bin/env python
"""
Script to update service charges for all events and recalculate ticket prices.
This script should be run after deploying the migrations.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from events.models import Event
from tickets.models import Ticket

# Update all events with correct service charges
events = Event.objects.all()
for event in events:
    event.normal_service_charge = 20  # 20% for normal users
    event.reseller_service_charge = 12  # 12% for resellers
    event.save()
    print(f"Updated event: {event.name}")

# Recalculate ticket prices for all tickets
tickets = Ticket.objects.all()
for ticket in tickets:
    ticket.save()  # This will trigger the price calculation in the save() method
    print(f"Recalculated prices for ticket: {ticket.id}")

print("All service charges and ticket prices have been updated!")
