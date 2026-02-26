from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponse, FileResponse
from django.views import View
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json
import os
from django.conf import settings

from .models import Order, Sale
from .forms import OrderForm, SaleForm, UploadTicketForm
from events.models import Ticket, Event


class OrderListView(LoginRequiredMixin, ListView):
    """View for buyers to see their purchased orders"""
    model = Order
    template_name = 'tickets/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')


class CreateOrderView(LoginRequiredMixin, CreateView):
    """View for creating a new order (buying a ticket)"""
    model = Order
    form_class = OrderForm
    template_name = 'tickets/create_order.html'
    success_url = reverse_lazy('tickets:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = self.kwargs.get('ticket_id')
        if ticket_id:
            context['ticket'] = get_object_or_404(Ticket, id=ticket_id)
        return context
    
    def form_valid(self, form):
        form.instance.buyer = self.request.user
        ticket_id = self.kwargs.get('ticket_id')
        if ticket_id:
            form.instance.ticket = get_object_or_404(Ticket, id=ticket_id)
        return super().form_valid(form)


class SaleListView(LoginRequiredMixin, ListView):
    """View for sellers to see their sales"""
    model = Sale
    template_name = 'tickets/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10
    
    def get_queryset(self):
        return Sale.objects.filter(seller=self.request.user).order_by('-created_at')


class UploadTicketView(LoginRequiredMixin, View):
    """View for sellers to upload ticket files"""
    
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            
            # Check if the user is the seller
            sale = Sale.objects.filter(order=order, seller=request.user).first()
            if not sale:
                return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
            
            # Handle file upload
            if 'ticket_file' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
            
            ticket_file = request.FILES['ticket_file']
            
            # Validate file type
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            file_ext = ticket_file.name.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                return JsonResponse({'success': False, 'error': 'Invalid file type'}, status=400)
            
            # Save the file
            order.ticket_file = ticket_file
            order.ticket_uploaded = True
            order.save()
            
            return JsonResponse({'success': True, 'message': 'Ticket uploaded successfully'})
        
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class DownloadTicketView(LoginRequiredMixin, View):
    """View for buyers to download their tickets"""
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            
            # Check if the user is the buyer
            if order.buyer != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Check if ticket file exists
            if not order.ticket_file:
                return JsonResponse({'error': 'Ticket file not available'}, status=404)
            
            try:
                file_obj = order.ticket_file
                file_name = str(file_obj.name)
                
                file_found = False
                file_content = None
                
                # Try local filesystem paths first (skip S3 if misconfigured)
                possible_paths = [
                    os.path.join(settings.MEDIA_ROOT, file_name),
                    os.path.join('/app/media', file_name),
                    os.path.join('/app', file_name),
                    file_name,
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        try:
                            with open(path, 'rb') as f:
                                file_content = f.read()
                            file_found = True
                            break
                        except:
                            pass
                
                if not file_found:
                    return JsonResponse({'error': 'Ticket file not found'}, status=404)
                
                # Serve the file
                response = HttpResponse(file_content, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{order.event_name}_ticket.pdf"'
                return response
            
            except Exception as file_error:
                import traceback
                return JsonResponse({'error': f'Error: {str(file_error)}'}, status=500)
        
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class MyTicketsView(LoginRequiredMixin, ListView):
    """View for buyers to see their purchased tickets"""
    model = Order
    template_name = 'tickets/my_tickets.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')
