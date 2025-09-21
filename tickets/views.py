import json
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin:
            context['base_template'] = 'accounts/superadmin_dashboard.html'
            return context
        user_type = self.request.user.user_type 
        if user_type=='Reseller':
            context['base_template'] = 'accounts/reseller_dashboard.html'
            return context

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, event_id=kwargs['event_id'])
        if not self.event:
            raise Http404("Event does not exist")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'event': self.event,
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.seller = self.request.user
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
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.request.user.email])
        send_mail(
            f"New Ticket Listed: {self.event.name}",
            f"Reseller {self.request.user.email} listed ticket {ticket.ticket_id}.",
            settings.DEFAULT_FROM_EMAIL,
            [settings.SUPERADMIN_EMAIL]
        )

        messages.success(self.request, "Ticket listing created successfully.")
        return redirect('events:my_listings')


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
            'ticket_types': dict(Ticket.ticket_type.field.choices),
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
        form.save()
        messages.success(self.request, "Ticket updated successfully.")
        return redirect('events:my_listings')


class ResellerTicketDeleteView(ResellerRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, seller=request.user)
        ticket.delete()
        messages.success(request, "Ticket deleted successfully.")
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
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        ticket.delete()
        messages.success(request, "Ticket deleted successfully.")
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

class RevolutAPI:
    
    def create_order(self, amount, currency, customer_email, description, order_id):
        url = f"https://merchant.revolut.com/api/orders"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Revolut-Api-Version': '2024-09-01',
            "Authorization": f"Bearer {settings.REVOLUT_API_KEY}",
        }
        payload = {
            "amount": int(amount * 100), 
            "currency": currency,
            "customer_email": customer_email,
            "description": description,
            "merchant_order_ext_ref": str(order_id),
            "capture_mode": "automatic",
            "redirect_url": settings.BASE_URL + reverse('events:payment_return') + "?status=success&order_id=" + str(order_id),
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        response.raise_for_status()
        return response.json()

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    slug_field = 'ticket_id'
    slug_url_kwarg = 'ticket_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        price_per_ticket = ticket.sell_price_for_reseller if self.request.user.user_type == 'Reseller' else ticket.sell_price_for_normal
        context['price_per_ticket'] = price_per_ticket
        context['total_price'] = ticket.number_of_tickets * price_per_ticket
        return context

class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, sold=False)
        
        price = ticket.sell_price_for_reseller if request.user.user_type == 'Reseller' else ticket.sell_price_for_normal
        total_price=ticket.number_of_tickets*price
        ticket_uploaded=False
        if ticket.upload_choice=='now':
            ticket_uploaded=True
        order = Order.objects.create(
            ticket_reference=ticket.ticket_id,
            event_name = ticket.event.name,
            event_date =ticket.event.date,
            event_time =ticket.event.time, 
            number_of_tickets = ticket.number_of_tickets,
            ticket_section =ticket.section.name,
            ticket_row =ticket.row,
            ticket_seats =ticket.seats,
            ticket_face_value = ticket.face_value,
            ticket_upload_type = ticket.ticket_type,
            ticket_benefits_and_Restrictions = ticket.benefits_and_Restrictions,
            ticket_sell_price = ticket.sell_price,
            ticket_uploaded=ticket_uploaded,
            buyer=request.user,
            amount=total_price,
            revolut_order_id="", 
            revolut_checkout_url=""
        )
        
        revolut_api = RevolutAPI()
        try:
            revolut_order = revolut_api.create_order(
                amount=total_price,
                currency="GBP", 
                customer_email=request.user.email,
                description=f"Ticket for {ticket.event.name}",
                order_id=order.id
            )
            
            order.revolut_order_id = revolut_order['id']
            order.revolut_checkout_url = revolut_order['checkout_url']
            order.save()
            
            return redirect(revolut_order['checkout_url'])
            
        except Exception as e:
            order.delete()
            messages.error(request, f"Payment processing error: {str(e)}")
            return redirect('events:ticket_detail', event_id=ticket.event.event_id, ticket_id=ticket.ticket_id)

class PaymentReturnView(LoginRequiredMixin, View):
    def get(self, request):
        status = request.GET.get('status')
        order_id = request.GET.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            
            if status == 'success':
                order.status = 'completed'
                order.save()
                
                ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
                ticket.sold = True
                ticket.buyer = request.user.email
                ticket.event.sold_tickets+=ticket.number_of_tickets
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
        subject = "Your Ticket Has Been Sold!"
        message = f"Your ticket for {order.event_name} has been purchased."
        
        if not order.ticket_uploaded:
            message += "\n\nPlease upload the ticket PDF as soon as possible."
            ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.seller.email]
            )
        else:
            message += "\n\nPayment will be processed after ticket verification."
            ticket = Ticket.objects.get(ticket_id=order.ticket_reference)
            
            send_mail(
                subject,
                message,
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
                    ticket.save()

                    self.send_notification_emails(ticket, request)

                    return JsonResponse({
                        'success': True,
                        'message': 'Ticket listing created successfully',
                        'ticket_id': str(ticket.ticket_id)
                    }, status=201)

            except Exception as e:
                return JsonResponse({'error': f'Error creating listing: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': form.errors}, status=400)

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
                form.save()
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

            ticket.delete()
            return JsonResponse({
                'success': True,
                'message': 'Ticket deleted successfully'
            })

        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        except Exception as e:
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
                'row': ticket.row,
                'seats': ticket.seats,
                'number_of_tickets': ticket.number_of_tickets,
                'ticket_type': ticket.ticket_type,
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
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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

        tickets = Ticket.objects.filter(event=event, sold=False)

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

        paginator = Paginator(tickets, per_page)

        try:
            tickets_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            tickets_page = paginator.page(1)
        user_type = request.user.user_type
        is_reseller = user_type == 'Reseller' or request.user.is_superadmin

        tickets_data = []
        for ticket in tickets_page:
            if is_reseller:
                price_per_ticket = ticket.sell_price_for_reseller
            else:
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
            })

        available_sections = event.sections.all().values('id', 'name', 'color')
        available_ticket_types = dict(Ticket.TICKET_TYPE_CHOICES)

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
                'sections': list(available_sections),
                'ticket_types': available_ticket_types,
                'applied': {
                    'sections': sections,
                    'ticket_types': ticket_types,
                    'min_price': min_price,
                    'max_price': max_price,
                    'number_of_tickets': number_of_tickets,
                }
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_tickets': paginator.count,
            }
        })
