import json
import uuid
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.mail import send_mail, EmailMessage
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseBadRequest, Http404,HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView,DetailView

from accounts.utils import api_login_required
from .models import Ticket,Sale,Order
from .forms import TicketForm
from events.models import EventSection, Event
from accounts.models import User
from django.conf import settings
import logging
import stripe
import requests
from .stripe_utils import StripeAPI

logger = logging.getLogger(__name__)

class ResellerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'Reseller'
    def handle_no_permission(self):
        messages.error(self.request, "You must be a Reseller to access that page.")
        return redirect('events:home')


class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superadmin
    def handle_no_permission(self):
        messages.error(self.request, "Unauthorized access")
        return redirect('accounts:sign_in')


class CreateListingView(ResellerRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/create_listing.html'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, event_id=kwargs['event_id'])
        
        # Check if event is expired (date/time is in the past)
        if self.event.is_expired:
            messages.error(request, f"Cannot create listing: The event '{self.event.name}' has already passed. Event date was {self.event.date.strftime('%B %d, %Y')} at {self.event.time.strftime('%I:%M %p')}.")
            return redirect('events:home')
        
        # Check if event has sections available, create default sections if not
        if not self.event.sections.exists():
            from events.models import EventSection
            default_sections = [
                {'name': 'General Admission', 'color': '#3CB44B', 'lower_price': 0, 'upper_price': 0},
                {'name': 'VIP', 'color': '#911EB4', 'lower_price': 0, 'upper_price': 0},
                {'name': 'Premium', 'color': '#F58231', 'lower_price': 0, 'upper_price': 0},
            ]
            for section_data in default_sections:
                EventSection.objects.create(
                    event=self.event,
                    name=section_data['name'],
                    color=section_data['color'],
                    lower_price=section_data['lower_price'],
                    upper_price=section_data['upper_price']
                )
            messages.success(request, f"Default sections have been created for '{self.event.name}'. You can now create a listing.")
            return redirect(request.path)
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
        else:
            user_type = self.request.user.user_type 
            if user_type == 'Reseller':
                context['base_template'] = 'accounts/reseller_dashboard.html'
            else:
                context['base_template'] = 'accounts/normal_dashboard.html'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'event': self.event,
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        try:
            # Double-check event is not expired (in case it changed between dispatch and form submission)
            if self.event.is_expired:
                messages.error(self.request, f"Cannot create listing: The event '{self.event.name}' has already passed. Event date was {self.event.date.strftime('%B %d, %Y')} at {self.event.time.strftime('%I:%M %p')}.")
                return self.form_invalid(form)
            
            # Validate event has sections
            if not self.event.sections.exists():
                messages.error(self.request, f"Cannot create listing: The event '{self.event.name}' has no sections available. Please contact the administrator.")
                return self.form_invalid(form)
            
            ticket = form.save(commit=False)
            ticket.seller = self.request.user
            ticket.event = self.event
            
            # Validate event and section are set
            if not ticket.event:
                messages.error(self.request, "Error: Event is required. Please try again.")
                return self.form_invalid(form)
            if not ticket.section:
                messages.error(self.request, "Error: Section is required. Please select a section.")
                return self.form_invalid(form)
            
            # Validate section belongs to event
            if ticket.section.event != ticket.event:
                messages.error(self.request, "Error: Selected section does not belong to this event. Please select a valid section.")
                return self.form_invalid(form)
            
            # Handle bundle creation if sell_together is checked
            if form.cleaned_data.get('sell_together', False):
                # Check if there's a bundle_id in session for this event
                session_key = f'bundle_id_{self.event.event_id}'
                bundle_id = self.request.session.get(session_key)
                
                # If no bundle_id in session, create a new one
                if not bundle_id:
                    bundle_id = uuid.uuid4()
                    self.request.session[session_key] = str(bundle_id)
                else:
                    bundle_id = uuid.UUID(bundle_id)
                
                ticket.bundle_id = bundle_id
            else:
                # Clear bundle_id from session if sell_together is not checked
                session_key = f'bundle_id_{self.event.event_id}'
                if session_key in self.request.session:
                    del self.request.session[session_key]
                ticket.bundle_id = None
            
            ticket.save()

            subject = f"Ticket Listing Created for {self.event.name}"
            marketplace_url = self.request.build_absolute_uri(
                reverse('events:event_tickets', args=[self.event.event_id])
            )
            message = (
                f"Your tickets have been listed.\n\n"
                f"Event: {self.event.name}\n"
                f"Ticket ID: {ticket.ticket_id}\n"
                f"View them here: {marketplace_url}"
            )
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.request.user.email])
                send_mail(
                    f"New Ticket Listed: {self.event.name}",
                    f"Reseller {self.request.user.email} listed ticket {ticket.ticket_id}.",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.SUPERADMIN_EMAIL]
                )
            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")
                # Don't fail the listing creation if email fails

            messages.success(self.request, "Ticket listing created successfully.")
            return redirect('events:my_listings')
        except ValueError as e:
            error_msg = str(e)
            if "date" in error_msg.lower() or "time" in error_msg.lower():
                messages.error(self.request, f"Cannot create listing: The event date/time is invalid or has passed. {error_msg}")
            else:
                messages.error(self.request, f"Validation error: {error_msg}")
            logger.error(f"Validation error creating ticket listing: {str(e)}")
            return self.form_invalid(form)
        except Exception as e:
            import traceback
            error_msg = str(e)
            logger.error(f"Error creating ticket listing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Provide user-friendly error messages
            if "expired" in error_msg.lower() or "past" in error_msg.lower():
                messages.error(self.request, f"Cannot create listing: The event '{self.event.name}' has already passed. Event date was {self.event.date.strftime('%B %d, %Y')} at {self.event.time.strftime('%I:%M %p')}.")
            elif "section" in error_msg.lower():
                messages.error(self.request, f"Cannot create listing: Section error. {error_msg}")
            elif "seats" in error_msg.lower():
                messages.error(self.request, f"Cannot create listing: Invalid seat information. Please check that the number of seats matches the number of tickets.")
            else:
                messages.error(self.request, f"Error creating ticket listing: {error_msg}. Please check all fields and try again.")
            return self.form_invalid(form)


class EventTicketListView(ListView):
    model = Ticket
    template_name = 'tickets/event_tickets.html'
    context_object_name = 'tickets'
    paginate_by = 100
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'tickets/_ticket_list.html', context)
        return super().get(request, *args, **kwargs)
    

    def get_queryset(self):
        qs = Ticket.objects.filter(
            event__event_id=self.kwargs['event_id'],
            sold=False
        )
        sections = self.request.GET.getlist('section')
        if sections:
            qs = qs.filter(section__id__in=sections)
        types = self.request.GET.getlist('ticket_type')
        if types:
            qs = qs.filter(ticket_type__in=types)
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            qs = qs.filter(sell_price__gte=min_price)
        if max_price:
            qs = qs.filter(sell_price__lte=max_price)
        nums = self.request.GET.getlist('number_of_tickets')
        if nums:
            qs = qs.filter(number_of_tickets__in=nums)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, event_id=self.kwargs['event_id'])
        ctx.update({
            'event': event,
            'sections': event.sections.all(),
            'ticket_types': dict(Ticket._meta.get_field('ticket_type').choices),
            'applied_filters': self.request.GET,
        })
        return ctx


class MyListingsView(ResellerRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/my_listings.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
        elif user_type=='Normal':
            context['base_template']='accounts/normal_dashboard'
        return context
        

    def get_queryset(self):
        return Ticket.objects.filter(seller=self.request.user).order_by('-created_at')


class ResellerTicketUpdateView(ResellerRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/reseller_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
        elif user_type=='Normal':
            context['base_template']='accounts/normal_dashboard'
        return context

    def get_object(self):
        ticket_id = self.kwargs['ticket_id']
        return get_object_or_404(
            Ticket,
            ticket_id=ticket_id,
            seller=self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'event': self.object.event,
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        ticket = self.get_object()
        # Check if PDF was just uploaded (wasn't there before, but is now)
        had_pdf_before = ticket.upload_file and ticket.upload_file.name
        form.save()
        ticket.refresh_from_db()
        has_pdf_now = ticket.upload_file and ticket.upload_file.name
        
        # If ticket is sold and PDF was just uploaded, send it to buyer
        if ticket.sold and ticket.buyer and not had_pdf_before and has_pdf_now:
            self.send_pdf_to_buyer(ticket)
        
        messages.success(self.request, "Ticket updated successfully.")
        return redirect('events:my_listings')
    
    def send_pdf_to_buyer(self, ticket):
        """Send PDF to buyer when reseller uploads it after purchase"""
        try:
            # Find the order for this ticket
            order = Order.objects.filter(
                ticket_reference=ticket.ticket_id,
                status='completed'
            ).first()
            
            if not order:
                return
            
            buyer_email = order.buyer.email
            buyer_subject = f"Your Ticket PDF for {order.event_name}"
            
            buyer_message = f"""Dear {order.buyer.first_name or 'Customer'},

Your ticket PDF has been uploaded by the seller and is now available!

Event: {order.event_name}
Date: {order.event_date.strftime('%B %d, %Y')}
Time: {order.event_time.strftime('%I:%M %p')}
Section: {order.ticket_section}
Row: {order.ticket_row}
Seats: {', '.join(order.ticket_seats)}

Your ticket PDF is attached to this email.

If you have any questions, please contact our support team.

Thank you!
"""
            
            # Read the PDF file
            try:
                pdf_file = ticket.upload_file
                pdf_file.open('rb')
                pdf_content = pdf_file.read()
                pdf_file.close()
                
                filename = f"ticket_{ticket.ticket_id}_{order.event_name.replace(' ', '_')}.pdf"
                
                # Send email with PDF attachment
                email = EmailMessage(
                    buyer_subject,
                    buyer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [buyer_email]
                )
                email.attach(filename, pdf_content, 'application/pdf')
                email.send()
                
            except Exception as e:
                logger.error(f"Error reading PDF for ticket {ticket.ticket_id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error sending PDF to buyer for ticket {ticket.ticket_id}: {str(e)}")


class ResellerTicketDeleteView(ResellerRequiredMixin, View):
    def get(self, request, ticket_id):
        # Redirect GET requests to my_listings with a message
        messages.info(request, "Please use the delete button on the listing page to delete tickets.")
        return redirect('events:my_listings')
    
    def post(self, request, ticket_id):
        try:
            ticket = get_object_or_404(Ticket, ticket_id=ticket_id, seller=request.user)
            
            # Check if ticket is sold - don't allow deletion of sold tickets
            if ticket.sold:
                messages.error(request, "Cannot delete listing: This ticket has already been sold and cannot be deleted.")
                return redirect('events:my_listings')
            
            # Store ticket info before deletion for logging
            ticket_info = {
                'ticket_id': str(ticket.ticket_id),
                'event_name': ticket.event.name,
                'number_of_tickets': ticket.number_of_tickets
            }
            
            # Delete the ticket (this will update event.total_tickets via the model's delete method)
            ticket.delete()
            
            messages.success(request, f"Ticket listing {ticket_info['ticket_id']} deleted successfully. The tickets are now available again.")
            return redirect('events:my_listings')
            
        except Http404:
            messages.error(request, "Ticket not found or you don't have permission to delete it.")
            return redirect('events:my_listings')
        except Exception as e:
            logger.error(f"Error deleting ticket {ticket_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"Error deleting ticket listing: {str(e)}")
            return redirect('events:my_listings')


class SuperadminTicketListView(SuperAdminRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/superadmin_list.html'
    context_object_name = 'tickets'
    paginate_by = 1

    def get_queryset(self):
        return Ticket.objects.select_related('event', 'seller').order_by('-created_at')


class SuperadminTicketUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/superadmin_update.html'

    def get_object(self):
        ticket_id = self.kwargs['ticket_id']
        return get_object_or_404(
            Ticket,
            ticket_id=ticket_id,
        ) 
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'event': self.object.event,
            'user': self.object.seller
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Ticket updated successfully.")
        return redirect('events:superadmin_list')


class SuperadminTicketDeleteView(SuperAdminRequiredMixin, View):
    def post(self, request, ticket_id):
        try:
            ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
            
            # Check if ticket is sold - warn but allow superadmin to delete
            if ticket.sold:
                messages.warning(request, f"Warning: Ticket {ticket.ticket_id} has been sold, but deletion was allowed for administrative purposes.")
            
            # Store ticket info before deletion
            ticket_info = {
                'ticket_id': str(ticket.ticket_id),
                'event_name': ticket.event.name,
                'number_of_tickets': ticket.number_of_tickets
            }
            
            # Delete the ticket
            ticket.delete()
            
            messages.success(request, f"Ticket listing {ticket_info['ticket_id']} deleted successfully.")
            return redirect('events:superadmin_list')
            
        except Exception as e:
            logger.error(f"Error deleting ticket {ticket_id}: {str(e)}")
            messages.error(request, f"Error deleting ticket listing: {str(e)}")
            return redirect('events:superadmin_list')


class ExpiredTicketListView(SuperAdminRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/superadmin_expired.html'
    context_object_name = 'tickets'
    paginate_by = 15

    def get_queryset(self):
        today = date.today()
        return Ticket.objects.filter(
            upload_choice='later',
            upload_by__lte=today
        ).order_by('upload_by')


class ExpiredTicketNotifyView(SuperAdminRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        subject = f"Upload Reminder: Ticket {ticket.ticket_id}"
        message = (
            f"Dear {ticket.seller.first_name},\n\n"
            f"Please upload your ticket PDF for event '{ticket.event.name}' by {ticket.upload_by}.\n"
            "Failure to upload may result in removal of your listing.\n\n"
            "Thank you."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ticket.seller.email])
        messages.success(request, "Reminder email sent to reseller.")
        return redirect('events:superadmin_expired')

class SectionPriceAjaxView(LoginRequiredMixin, View):
    def get(self, request):
        section_id = request.GET.get('section_id')
        try:
            sec = EventSection.objects.get(id=section_id)
            return JsonResponse({
                'lower_price':int(sec.lower_price),
                'upper_price': int(sec.upper_price),
            })
        except EventSection.DoesNotExist:
            return JsonResponse({'error': 'Section not found'}, status=404)


import requests
from django.conf import settings
from django.urls import reverse
from .models import Order, Sale

# RevolutAPI class has been replaced with StripeAPI
# See stripe_utils.py for the new Stripe payment implementation

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    slug_field = 'ticket_id'
    slug_url_kwarg = 'ticket_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        # Determine user type safely
        user_type = getattr(self.request.user, 'user_type', 'Normal')
        is_reseller = user_type == 'Reseller' or self.request.user.is_superadmin
        price_per_ticket = ticket.sell_price_for_reseller if is_reseller else ticket.sell_price_for_normal
        
        # Check if ticket is part of a bundle
        if ticket.is_bundled:
            bundle_tickets = ticket.get_bundle_tickets()
            context['is_bundled'] = True
            context['bundle_tickets'] = bundle_tickets
            # Calculate total price for all tickets in bundle
            total_price = sum(
                t.number_of_tickets * (t.sell_price_for_reseller if is_reseller else t.sell_price_for_normal)
                for t in bundle_tickets
            )
            context['total_price'] = total_price
        else:
            context['is_bundled'] = False
            context['price_per_ticket'] = price_per_ticket
            context['total_price'] = ticket.number_of_tickets * price_per_ticket
        
        # Add user type info to context so template can use it
        context['is_reseller'] = is_reseller
        context['user_type'] = user_type
        
        return context

class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, sold=False)
        
        # Determine user type safely
        user_type = getattr(request.user, 'user_type', 'Normal')
        is_reseller = user_type == 'Reseller' or request.user.is_superadmin
        
        # Check if ticket is part of a bundle
        if ticket.is_bundled:
            # Get all tickets in the bundle
            bundle_tickets = list(ticket.get_bundle_tickets())
            
            # Validate all tickets in bundle are available
            for t in bundle_tickets:
                if t.sold:
                    messages.error(request, "One or more tickets in this bundle are no longer available.")
                    return redirect('events:event_tickets', event_id=ticket.event.event_id)
            
            # Calculate total price for bundle
            price = sum(
                t.number_of_tickets * (t.sell_price_for_reseller if is_reseller else t.sell_price_for_normal)
                for t in bundle_tickets
            )
            total_price = price
            
            # Create order with bundle information
            ticket_uploaded = all(t.upload_choice == 'now' for t in bundle_tickets)
            
            # Store bundle ticket references as JSON
            bundle_ticket_refs = [str(t.ticket_id) for t in bundle_tickets]
            
            order = Order.objects.create(
                ticket_reference=ticket.ticket_id,  # Primary ticket reference
                event_name=ticket.event.name,
                event_date=ticket.event.date,
                event_time=ticket.event.time,
                number_of_tickets=sum(t.number_of_tickets for t in bundle_tickets),
                ticket_section=ticket.section.name,
                ticket_row=ticket.row,
                ticket_seats=ticket.seats,  # Will store first ticket's seats
                ticket_face_value=ticket.face_value,
                ticket_upload_type=ticket.ticket_type,
                ticket_benefits_and_Restrictions=ticket.benefits_and_Restrictions,
                ticket_sell_price=ticket.sell_price,
                ticket_uploaded=ticket_uploaded,
                buyer=request.user,
                amount=total_price,
                revolut_order_id="",
                revolut_checkout_url=""
            )
        else:
            # Individual ticket purchase (existing logic)
            requested_quantity = int(request.POST.get('quantity', ticket.number_of_tickets))
            
            # Handle partial purchase if sell_together is False
            if not ticket.sell_together and requested_quantity < ticket.number_of_tickets:
                # Create a new ticket for the sold portion
                new_seats = ticket.seats[:requested_quantity]
                remaining_seats = ticket.seats[requested_quantity:]
                
                # Update original ticket (remaining portion)
                ticket.number_of_tickets -= requested_quantity
                ticket.seats = remaining_seats
                ticket.save()
                
                # Create new ticket instance for the order
                ticket = Ticket.objects.create(
                    event=ticket.event,
                    seller=ticket.seller,
                    buyer=request.user.email, # Will be confirmed on payment
                    number_of_tickets=requested_quantity,
                    section=ticket.section,
                    row=ticket.row,
                    seats=new_seats,
                    face_value=ticket.face_value,
                    ticket_type=ticket.ticket_type,
                    benefits_and_Restrictions=ticket.benefits_and_Restrictions,
                    sell_price=ticket.sell_price,
                    sell_together=False, # It's a split ticket now
                    upload_choice=ticket.upload_choice,
                    upload_by=ticket.upload_by,
                    # upload_file logic tricky if splitting file? inheriting for now
                )
            
            price = ticket.sell_price_for_reseller if is_reseller else ticket.sell_price_for_normal
            total_price = ticket.number_of_tickets * price
            ticket_uploaded = False
            if ticket.upload_choice == 'now':
                ticket_uploaded = True
            
            order = Order.objects.create(
                ticket_reference=ticket.ticket_id,
                event_name=ticket.event.name,
                event_date=ticket.event.date,
                event_time=ticket.event.time,
                number_of_tickets=ticket.number_of_tickets,
                ticket_section=ticket.section.name,
                ticket_row=ticket.row,
                ticket_seats=ticket.seats,
                ticket_face_value=ticket.face_value,
                ticket_upload_type=ticket.ticket_type,
                ticket_benefits_and_Restrictions=ticket.benefits_and_Restrictions,
                ticket_sell_price=ticket.sell_price,
                ticket_uploaded=ticket_uploaded,
                buyer=request.user,
                amount=total_price,
                revolut_order_id="",
                revolut_checkout_url=""
            )
        
        # Check if Stripe is configured
        is_configured, config_message = StripeAPI.validate_config()
        if not is_configured:
            order.delete()
            messages.error(request, f"Payment system is not configured: {config_message}. Please contact support.")
            return redirect('events:ticket_detail', event_id=ticket.event.event_id, ticket_id=ticket.ticket_id)
        
        try:
            stripe_api = StripeAPI()
            stripe_session = stripe_api.create_checkout_session(
                amount=total_price,
                currency="GBP",
                customer_email=request.user.email,
                description=f"Ticket for {ticket.event.name}",
                order_id=order.id
            )
            
            order.stripe_session_id = stripe_session['session_id']
            order.stripe_payment_intent_id = stripe_session['payment_intent_id']
            order.save()
            
            return redirect(stripe_session['checkout_url'])
            
        except ValueError as e:
            order.delete()
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('events:ticket_detail', event_id=ticket.event.event_id, ticket_id=ticket.ticket_id)
        except Exception as e:
            order.delete()
            logger.error(f"Unexpected error during payment processing: {str(e)}")
            messages.error(request, f"Payment processing error: {str(e)}. Please try again or contact support.")
            return redirect('events:ticket_detail', event_id=ticket.event.event_id, ticket_id=ticket.ticket_id)

class PaymentReturnView(LoginRequiredMixin, View):
    def get(self, request):
        status = request.GET.get('status')
        order_id = request.GET.get('order_id')
        session_id = request.GET.get('session_id')
        
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            
            if status == 'success':
                # Verify the Stripe session
                if session_id:
                    try:
                        stripe_api = StripeAPI()
                        session = stripe_api.retrieve_session(session_id)
                        if session.payment_status != 'paid':
                            order.status = 'failed'
                            order.save()
                            messages.error(request, "Payment verification failed.")
                            return redirect('events:home')
                    except Exception as e:
                        logger.error(f"Error verifying Stripe session: {str(e)}")
                        order.status = 'failed'
                        order.save()
                        messages.error(request, "Payment verification error.")
                        return redirect('events:home')
                order.status = 'completed'
                order.save()
                
                ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
                
                # Check if ticket is part of a bundle
                if ticket.is_bundled:
                    # Mark all tickets in the bundle as sold
                    bundle_tickets = ticket.get_bundle_tickets()
                    total_tickets_count = 0
                    
                    for t in bundle_tickets:
                        t.sold = True
                        t.buyer = request.user.email
                        t.save()
                        total_tickets_count += t.number_of_tickets
                    
                    # Update event sold tickets count
                    ticket.event.sold_tickets += total_tickets_count
                    ticket.event.save()
                else:
                    # Individual ticket
                    ticket.sold = True
                    ticket.buyer = request.user.email
                    ticket.event.sold_tickets += ticket.number_of_tickets
                    ticket.save()
                    ticket.event.save()
                
                self.send_notifications(order)
                
                messages.success(request, "Payment successful! Your tickets are secured.")
                return redirect('events:my_orders')
                
            else:
                order.status = 'failed'
                order.save()
                messages.error(request, "Payment failed. Please try again.")
                return redirect('events:home')
                
        except Order.DoesNotExist:
            messages.error(request, "Invalid order")
            return redirect('events:home')
    
    def send_notifications(self, order):
        ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
        
        # Send email to seller
        seller_subject = "Your Ticket Has Been Sold!"
        seller_message = f"Your ticket for {order.event_name} has been purchased."
        
        if not order.ticket_uploaded:
            seller_message += "\n\nPlease upload the ticket PDF as soon as possible."
            send_mail(
                seller_subject,
                seller_message,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.seller.email]
            )
        else:
            seller_message += "\n\nPayment will be processed after ticket verification."
            send_mail(
                seller_subject,
                seller_message,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.seller.email]
            )
            
            admin_subject = f"Payout Required for Order {order.id}"
            admin_message = f"Ticket {ticket.ticket_id} has been sold and requires payout to the seller."
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPERADMIN_EMAIL]
            )
        
        # Send email to buyer with PDF if available
        self.send_buyer_notification(order, ticket)
    
    def send_buyer_notification(self, order, ticket):
        """Send confirmation email to buyer with PDF attachment if available"""
        buyer_email = order.buyer.email
        buyer_subject = f"Your Tickets for {order.event_name}"
        
        buyer_message = f"""Dear {order.buyer.first_name or 'Customer'},

Thank you for your purchase!

Your order details:
- Event: {order.event_name}
- Date: {order.event_date.strftime('%B %d, %Y')}
- Time: {order.event_time.strftime('%I:%M %p')}
- Section: {order.ticket_section}
- Row: {order.ticket_row}
- Seats: {', '.join(order.ticket_seats)}
- Number of Tickets: {order.number_of_tickets}
- Order ID: {order.id}

"""
        
        # Check if ticket is part of a bundle
        if ticket.is_bundled:
            bundle_tickets = ticket.get_bundle_tickets()
            buyer_message += "\nThis purchase includes multiple tickets in a bundle.\n"
        else:
            bundle_tickets = [ticket]
        
        # Check if PDFs are available and attach them
        pdf_attachments = []
        tickets_with_pdf = []
        tickets_without_pdf = []
        
        for t in bundle_tickets:
            if t.upload_file and t.upload_file.name:
                try:
                    # Open the PDF file from S3
                    pdf_file = t.upload_file
                    pdf_file.open('rb')
                    pdf_content = pdf_file.read()
                    pdf_file.close()
                    
                    # Create attachment
                    filename = f"ticket_{t.ticket_id}_{order.event_name.replace(' ', '_')}.pdf"
                    pdf_attachments.append((filename, pdf_content, 'application/pdf'))
                    tickets_with_pdf.append(t)
                except Exception as e:
                    logger.error(f"Error reading PDF for ticket {t.ticket_id}: {str(e)}")
                    tickets_without_pdf.append(t)
            else:
                tickets_without_pdf.append(t)
        
        if tickets_with_pdf:
            buyer_message += f"\nYour ticket PDF{'s' if len(tickets_with_pdf) > 1 else ''} {'are' if len(tickets_with_pdf) > 1 else 'is'} attached to this email.\n"
        
        if tickets_without_pdf:
            buyer_message += f"\nNote: Some ticket PDF{'s' if len(tickets_without_pdf) > 1 else ''} will be sent to you once the seller uploads {'them' if len(tickets_without_pdf) > 1 else 'it'}.\n"
        
        buyer_message += "\nIf you have any questions, please contact our support team.\n\nThank you for choosing our service!"
        
        try:
            if pdf_attachments:
                # Use EmailMessage to send with attachments
                email = EmailMessage(
                    buyer_subject,
                    buyer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [buyer_email]
                )
                
                # Attach all PDFs
                for filename, content, content_type in pdf_attachments:
                    email.attach(filename, content, content_type)
                
                email.send()
            else:
                # No PDFs available, send regular email
                send_mail(
                    buyer_subject,
                    buyer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [buyer_email]
                )
        except Exception as e:
            logger.error(f"Error sending buyer notification email: {str(e)}")
            # Don't fail the order if email fails, but log it

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'tickets/order_list.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
            return context
        elif user_type=='Normal':
            context['base_template']='accounts/normal_dashboard.html'
        
        orders_with_ticket_info = []
        for order in context['orders']:
            ticket_upload_choice = None
            try:
                ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
                ticket_upload_choice = ticket.upload_choice
                print(ticket_upload_choice)
            except Ticket.DoesNotExist:
                ticket_upload_choice = 'Ticket Not Found/Deleted'
            except ValueError:
                ticket_upload_choice = 'Invalid Ticket Reference'

            orders_with_ticket_info.append({
                'order': order,
                'ticket_upload_choice': ticket_upload_choice,
            })
        context['orders'] = orders_with_ticket_info
        
        return context
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user,status='completed').order_by('-created_at')

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'tickets/sale_list.html'
    context_object_name = 'sales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
            return context
    
    def get_queryset(self):
        return Sale.objects.filter(seller=self.request.user).order_by('-created_at')

class SuperadminOrderListView(SuperAdminRequiredMixin, ListView):
    model = Order
    template_name = 'tickets/superadmin_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
            return context
        
        orders_with_ticket_info = []
        for order in context['orders']:
            ticket_upload_choice = None
            try:
                ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
                order.ticket_upload_choice = ticket.upload_choice
            except Ticket.DoesNotExist:
                order.ticket_upload_choice = 'Ticket Not Found/Deleted'
            except ValueError:
                order.ticket_upload_choice = 'Invalid Ticket Reference'

            orders_with_ticket_info.append(order)
        context['orders'] = orders_with_ticket_info
        
        return context
    
    def get_queryset(self):
        queryset=Order.objects.filter(status='completed').order_by('-created_at')
        orders_to_update = []
        for order in queryset:
            try:
                ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
                should_be_uploaded = (ticket.upload_choice == 'now')
                if order.ticket_uploaded != should_be_uploaded:
                    order.ticket_uploaded = should_be_uploaded
                    orders_to_update.append(order)

            except Ticket.DoesNotExist:
                if order.ticket_uploaded:
                    order.ticket_uploaded = False
                    orders_to_update.append(order)
            except ValueError:
                if order.ticket_uploaded:
                    order.ticket_uploaded = False
                    orders_to_update.append(order)
        if orders_to_update:
            Order.objects.bulk_update(orders_to_update, ['ticket_uploaded'])
        return queryset

class SuperadminSaleListView(SuperAdminRequiredMixin, ListView):
    model = Sale
    template_name = 'tickets/superadmin_sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def get_queryset(self):
        return Sale.objects.all().order_by('-created_at')

class MarkAsPaidView(SuperAdminRequiredMixin, View):
    def get(self, request, order_id):
        return self.process_payment(request, order_id)
    
    def post(self, request, order_id):
        return self.process_payment(request, order_id)
    
    def process_payment(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
            
            sale, created = Sale.objects.get_or_create(
                order=order,
                defaults={
                    'seller': ticket.seller,
                    'amount': ticket.sell_price, 
                    'payout_date': timezone.now().date()
                }
            )
            
            order.paid_to_reseller = True
            order.save()
            
            send_mail(
                "Payment Processed",
                f"Your payment for ticket {ticket.ticket_id} has been processed.",
                settings.DEFAULT_FROM_EMAIL,
                [ticket.seller.email]
            )
            
            messages.success(request, "Payment marked as completed")
            return redirect('events:superadmin_orders')
            
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('events:superadmin_orders')


class CreateListingAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, event_id):
        if request.user.user_type != 'Reseller' and not request.user.is_superadmin:
            return JsonResponse({'error': 'Only resellers can create listings'}, status=403)

        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

        # Check if event is expired (date/time is in the past)
        if event.is_expired:
            return JsonResponse({
                'error': f"Cannot create listing: The event '{event.name}' has already passed. Event date was {event.date.strftime('%B %d, %Y')} at {event.time.strftime('%I:%M %p')}."
            }, status=400)

        # Check if event has sections available
        if not event.sections.exists():
            return JsonResponse({
                'error': f"Cannot create listing: The event '{event.name}' has no sections available. Please contact the administrator."
            }, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if 'seats' in data and isinstance(data['seats'], str):
            data['seats'] = [s.strip() for s in data['seats'].split(',') if s.strip()]

        if 'benefits_and_Restrictions' in data and isinstance(data['benefits_and_Restrictions'], str):
            data['benefits_and_Restrictions'] = [b.strip() for b in data['benefits_and_Restrictions'].split(',') if
                                                 b.strip()]

        form = TicketForm(data, event=event, user=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():
                    ticket = form.save(commit=False)
                    ticket.seller = request.user
                    ticket.event = event
                    
                    # Validate event and section are set
                    if not ticket.event:
                        return JsonResponse({'error': 'Event is required. Please try again.'}, status=400)
                    if not ticket.section:
                        return JsonResponse({'error': 'Section is required. Please select a section.'}, status=400)
                    
                    # Validate section belongs to event
                    if ticket.section.event != ticket.event:
                        return JsonResponse({'error': 'Selected section does not belong to this event. Please select a valid section.'}, status=400)
                    
                    # Double-check event is not expired
                    if event.is_expired:
                        return JsonResponse({
                            'error': f"Cannot create listing: The event '{event.name}' has already passed. Event date was {event.date.strftime('%B %d, %Y')} at {event.time.strftime('%I:%M %p')}."
                        }, status=400)
                    
                    ticket.save()

                    #self.send_notification_emails(ticket, request)

                    return JsonResponse({
                        'success': True,
                        'message': 'Ticket listing created successfully',
                        'ticket_id': str(ticket.ticket_id)
                    }, status=201)

            except ValueError as e:
                error_msg = str(e)
                if "date" in error_msg.lower() or "time" in error_msg.lower() or "expired" in error_msg.lower() or "past" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: The event date/time is invalid or has passed. {error_msg}"
                    }, status=400)
                elif "section" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: Section error. {error_msg}"
                    }, status=400)
                elif "seats" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: Invalid seat information. Please check that the number of seats matches the number of tickets."
                    }, status=400)
                else:
                    return JsonResponse({'error': f'Validation error: {error_msg}'}, status=400)
            except Exception as e:
                error_msg = str(e)
                if "expired" in error_msg.lower() or "past" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: The event '{event.name}' has already passed. Event date was {event.date.strftime('%B %d, %Y')} at {event.time.strftime('%I:%M %p')}."
                    }, status=400)
                elif "section" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: Section error. {error_msg}"
                    }, status=400)
                elif "seats" in error_msg.lower():
                    return JsonResponse({
                        'error': f"Cannot create listing: Invalid seat information. Please check that the number of seats matches the number of tickets."
                    }, status=400)
                else:
                    return JsonResponse({'error': f'Error creating listing: {error_msg}. Please check all fields and try again.'}, status=500)
        else:
            # Format form errors for better user experience
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if "date" in str(error).lower() or "time" in str(error).lower():
                        error_messages.append(f"Event date/time issue: {error}")
                    elif "section" in str(error).lower():
                        error_messages.append(f"Section issue: {error}")
                    elif "seats" in str(error).lower():
                        error_messages.append(f"Seat information issue: {error}")
                    else:
                        error_messages.append(f"{field}: {error}")
            
            return JsonResponse({
                'error': ' '.join(error_messages) if error_messages else 'Please check all fields and try again.',
                'form_errors': form.errors
            }, status=400)

    def send_notification_emails(self, ticket, request):
        subject = f"Ticket Listing Created for {ticket.event.name}"
        marketplace_url = request.build_absolute_uri(
            reverse('events:event_tickets', args=[ticket.event.event_id])
        )
        message = (
            f"Your tickets have been listed.\n\n"
            f"Event: {ticket.event.name}\n"
            f"Ticket ID: {ticket.ticket_id}\n"
            f"View them here: {marketplace_url}"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
        except Exception as e:
            logger.error(f"Failed to send email to seller: {str(e)}")

        admin_subject = f"New Ticket Listed: {ticket.event.name}"
        admin_message = (
            f"Reseller {request.user.email} listed ticket {ticket.ticket_id}.\n"
            f"Event: {ticket.event.name}\n"
            f"Section: {ticket.section.name}\n"
            f"Seats: {', '.join(ticket.seats)}\n"
            f"Price: ${ticket.sell_price}"
        )

        try:
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPERADMIN_EMAIL]
            )
        except Exception as e:
            logger.error(f"Failed to send email to admin: {str(e)}")


class TicketUpdateAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)

            if ticket.seller != request.user and not request.user.is_superadmin:
                return JsonResponse({'error': 'You can only update your own listings'}, status=403)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

            if 'seats' in data and isinstance(data['seats'], str):
                data['seats'] = [s.strip() for s in data['seats'].split(',') if s.strip()]

            if 'benefits_and_Restrictions' in data and isinstance(data['benefits_and_Restrictions'], str):
                data['benefits_and_Restrictions'] = [b.strip() for b in data['benefits_and_Restrictions'].split(',') if
                                                     b.strip()]

            form = TicketForm(data, instance=ticket, event=ticket.event, user=request.user)

            if form.is_valid():
                # Check if PDF was just uploaded (wasn't there before, but is now)
                had_pdf_before = ticket.upload_file and ticket.upload_file.name
                form.save()
                ticket.refresh_from_db()
                has_pdf_now = ticket.upload_file and ticket.upload_file.name
                
                # If ticket is sold and PDF was just uploaded, send it to buyer
                if ticket.sold and ticket.buyer and not had_pdf_before and has_pdf_now:
                    self.send_pdf_to_buyer_api(ticket)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Ticket updated successfully',
                    'ticket_id': str(ticket.ticket_id)
                })
            else:
                return JsonResponse({'error': form.errors}, status=400)
        
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error updating ticket: {str(e)}'}, status=500)
    
    def send_pdf_to_buyer_api(self, ticket):
        """Send PDF to buyer when reseller uploads it after purchase (API version)"""
        try:
            # Find the order for this ticket
            order = Order.objects.filter(
                ticket_reference=ticket.ticket_id,
                status='completed'
            ).first()
            
            if not order:
                return
            
            buyer_email = order.buyer.email
            buyer_subject = f"Your Ticket PDF for {order.event_name}"
            
            buyer_message = f"""Dear {order.buyer.first_name or 'Customer'},

Your ticket PDF has been uploaded by the seller and is now available!

Event: {order.event_name}
Date: {order.event_date.strftime('%B %d, %Y')}
Time: {order.event_time.strftime('%I:%M %p')}
Section: {order.ticket_section}
Row: {order.ticket_row}
Seats: {', '.join(order.ticket_seats)}

Your ticket PDF is attached to this email.

If you have any questions, please contact our support team.

Thank you!
"""
            
            # Read the PDF file
            try:
                pdf_file = ticket.upload_file
                pdf_file.open('rb')
                pdf_content = pdf_file.read()
                pdf_file.close()
                
                filename = f"ticket_{ticket.ticket_id}_{order.event_name.replace(' ', '_')}.pdf"
                
                # Send email with PDF attachment
                email = EmailMessage(
                    buyer_subject,
                    buyer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [buyer_email]
                )
                email.attach(filename, pdf_content, 'application/pdf')
                email.send()
                
            except Exception as e:
                logger.error(f"Error reading PDF for ticket {ticket.ticket_id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error sending PDF to buyer for ticket {ticket.ticket_id}: {str(e)}")


class TicketDetailAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)

            can_view = (
                    ticket.seller == request.user or
                    request.user.is_superadmin or
                    (hasattr(ticket, 'order') and ticket.order.buyer == request.user)
            )

            if not can_view:
                return JsonResponse({'error': 'Access denied'}, status=403)

            if request.user.user_type == 'Reseller':
                price_per_ticket = ticket.sell_price_for_reseller
            else:
                price_per_ticket = ticket.sell_price_for_normal

            ticket_data = {
                'ticket_id': str(ticket.ticket_id),
                'event': {
                    'event_id': ticket.event.event_id,
                    'name': ticket.event.name,
                    'date': ticket.event.date.isoformat(),
                    'time': ticket.event.time.strftime('%H:%M:%S'),
                    'stadium_name': ticket.event.stadium_name,
                },
                'section': {
                    'id': ticket.section.id,
                    'name': ticket.section.name,
                    'color': ticket.section.color,
                },
                'row': ticket.row,
                'seats': ticket.seats,
                'number_of_tickets': ticket.number_of_tickets,
                'face_value': float(ticket.face_value),
                'ticket_type': ticket.ticket_type,
                'benefits_and_Restrictions': ticket.benefits_and_Restrictions,
                'sell_together': ticket.sell_together,
                'sell_price': float(ticket.sell_price),
                'price_per_ticket': float(price_per_ticket),
                'total_price': float(ticket.number_of_tickets * price_per_ticket),
                'upload_choice': ticket.upload_choice,
                'upload_by': ticket.upload_by.isoformat() if ticket.upload_by else None,
                'created_at': ticket.created_at.isoformat(),
                'seller': {
                    'email': ticket.seller.email,
                    'first_name': ticket.seller.first_name,
                    'last_name': ticket.seller.last_name,
                }
            }

            return JsonResponse(ticket_data)

        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)

class SectionPriceAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        section_id = request.GET.get('section_id')
        try:
            section = EventSection.objects.get(id=section_id)
            return JsonResponse({
                'lower_price': float(section.lower_price),
                'upper_price': float(section.upper_price),
            })
        except EventSection.DoesNotExist:
            return JsonResponse({'error': 'Section not found'}, status=404)


class TicketDeleteAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)

            if ticket.seller != request.user and not request.user.is_superadmin:
                return JsonResponse({'error': 'You can only delete your own listings'}, status=403)

            # Check if ticket is sold - don't allow deletion of sold tickets (unless superadmin)
            if ticket.sold and not request.user.is_superadmin:
                return JsonResponse({
                    'error': 'Cannot delete listing: This ticket has already been sold and cannot be deleted.'
                }, status=400)

            # Store ticket info before deletion
            ticket_info = {
                'ticket_id': str(ticket.ticket_id),
                'event_name': ticket.event.name,
                'number_of_tickets': ticket.number_of_tickets,
                'sold': ticket.sold
            }
            
            # Delete the ticket
            ticket.delete()
            
            if ticket_info['sold'] and request.user.is_superadmin:
                return JsonResponse({
                    'success': True,
                    'message': f"Ticket listing {ticket_info['ticket_id']} deleted successfully (was sold, but deletion allowed for admin)."
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': f"Ticket listing {ticket_info['ticket_id']} deleted successfully. The tickets are now available again."
                })

        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting ticket {ticket_id}: {str(e)}")
            return JsonResponse({'error': f'Error deleting ticket: {str(e)}'}, status=500)


class MyListingsAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        if request.user.user_type != 'Reseller' and not request.user.is_superadmin:
            return JsonResponse({'error': 'Only resellers can view listings'}, status=403)

        status_filter = request.GET.get('status', 'all') 
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        tickets = Ticket.objects.filter(seller=request.user)

        if status_filter == 'active':
            tickets = tickets.filter(sold=False)
        elif status_filter == 'sold':
            tickets = tickets.filter(sold=True)

        tickets = tickets.order_by('-created_at')

        paginator = Paginator(tickets, per_page)

        try:
            tickets_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            tickets_page = paginator.page(1)

        tickets_data = []
        for ticket in tickets_page:
            tickets_data.append({
                'ticket_id': str(ticket.ticket_id),
                'event': {
                    'event_id': ticket.event.event_id,
                    'name': ticket.event.name,
                    'date': ticket.event.date.isoformat(),
                    'time': ticket.event.time.strftime('%H:%M:%S'),
                },
                'section': ticket.section.name,
                'section_id':ticket.section.id,
                'row': ticket.row,
                'seats': ticket.seats,
                'number_of_tickets': ticket.number_of_tickets,
                'ticket_type': ticket.ticket_type,
                'sell_together': ticket.sell_together,
                'face_value':ticket.face_value,
                'sell_price': float(ticket.sell_price),
                'created_at': ticket.created_at.isoformat(),
                'sold': ticket.sold,
                'upload_choice': ticket.upload_choice,
                'upload_by': ticket.upload_by.isoformat() if ticket.upload_by else None,
            })

        return JsonResponse({
            'tickets': tickets_data,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_tickets': paginator.count,
            'filters': {
                'status': status_filter
            }
        })


class EventTicketListAPIView(View):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

        sections = request.GET.getlist('section')
        ticket_types = request.GET.getlist('ticket_type')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        number_of_tickets = request.GET.getlist('number_of_tickets')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 100))

        tickets = Ticket.objects.filter(event=event, sold=False).order_by('sell_price_for_normal')

        if sections:
            tickets = tickets.filter(section__id__in=sections)

        if ticket_types:
            tickets = tickets.filter(ticket_type__in=ticket_types)

        if min_price:
            try:
                tickets = tickets.filter(sell_price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                tickets = tickets.filter(sell_price__lte=float(max_price))
            except ValueError:
                pass

        if number_of_tickets:
            try:
                tickets = tickets.filter(number_of_tickets__in=[int(n) for n in number_of_tickets])
            except ValueError:
                pass

        tickets = tickets.order_by('-created_at')

        # Pagination removed as per request - return all data
        if request.user.is_authenticated:
            user_type = request.user.user_type
            is_reseller = user_type == 'Reseller' or request.user.is_superadmin
        else:
            user_type = None
            is_reseller = False

        tickets_data = []
        for ticket in tickets:
            price_per_ticket = ticket.sell_price_for_normal

            tickets_data.append({
                'ticket_id': str(ticket.ticket_id),
                'section': {
                    'id': ticket.section.id,
                    'name': ticket.section.name,
                    'color': ticket.section.color,
                },
                'row': ticket.row,
                'seats': ticket.seats,
                'number_of_tickets': ticket.number_of_tickets,
                'face_value': float(ticket.face_value),
                'ticket_type': ticket.ticket_type,
                'benefits_and_Restrictions': ticket.benefits_and_Restrictions,
                'sell_price': float(ticket.sell_price),
                'price_per_ticket': float(price_per_ticket),
                'total_price': float(ticket.number_of_tickets * price_per_ticket),
                'upload_choice': ticket.upload_choice,
                'upload_by': ticket.upload_by.isoformat() if ticket.upload_by else None,
                'created_at': ticket.created_at.isoformat(),
                'sell_together': ticket.sell_together,
            })

        available_sections = event.sections.all().values('id', 'name', 'color')
        available_ticket_types = dict(Ticket.TICKET_TYPE_CHOICES)
        
        # Import section normalization function
        from events.stadium_config import normalize_section_name
        
        # Add SVG section key for mapping
        sections_with_svg = []
        for section in available_sections:
            sections_with_svg.append({
                'id': section['id'],
                'name': section['name'],
                'color': section['color'],
                'svg_section_key': normalize_section_name(section['name']),
            })

        return JsonResponse({
            'event': {
                'event_id': event.event_id,
                'name': event.name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M:%S'),
                'stadium_name': event.stadium_name,
                'stadium_image': event.stadium_image,
                'event_logo': event.event_logo,
            },
            'tickets': tickets_data,
            'filters': {
                'sections': sections_with_svg,
                'ticket_types': available_ticket_types,
                'applied': {
                    'sections': sections,
                    'ticket_types': ticket_types,
                    'min_price': min_price,
                    'max_price': max_price,
                    'number_of_tickets': number_of_tickets,
                }
            }
        })
