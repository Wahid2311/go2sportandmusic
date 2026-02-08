import json
from datetime import datetime, date, time
from django.core import serializers
from django.db import transaction
from django.views import View
from django.urls import reverse,reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Min, Max
from django.views.generic import CreateView, ListView, UpdateView,TemplateView
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, Count, Sum
from django.core.exceptions import ValidationError
from .models import Event, EventSection, ContactMessage, Category
from .forms import EventCreationForm, SectionForm, EventSearchForm,ContactForm
from accounts.utils import api_login_required, require_user_type, authenticate_via_id_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from tickets.models import Ticket


class SuperAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superadmin
    
    def handle_no_permission(self):
        messages.error(self.request, "Unauthorized access")
        return redirect(reverse('accounts:sign_in'))

class EventCreateAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        if not request.user.is_superadmin:
            return JsonResponse({'error': 'Only superadmins can create events'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Validate required fields
        required_fields = ['name', 'category', 'stadium_name', 'stadium_image', 'event_logo', 'date', 'time']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JsonResponse({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        try:
            # Parse date string to date object
            date_str = data.get('date')
            if isinstance(date_str, str):
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                    except (ValueError, AttributeError):
                        return JsonResponse({'error': f'Invalid date format: {date_str}. Expected YYYY-MM-DD'}, status=400)
            elif isinstance(date_str, date):
                parsed_date = date_str
            else:
                return JsonResponse({'error': 'Date must be a string in YYYY-MM-DD format'}, status=400)
            
            # Parse time string to time object
            time_str = data.get('time')
            if isinstance(time_str, str):
                try:
                    # Try HH:MM:SS format first
                    parsed_time = datetime.strptime(time_str, '%H:%M:%S').time()
                except ValueError:
                    try:
                        # Try HH:MM format
                        parsed_time = datetime.strptime(time_str, '%H:%M').time()
                    except ValueError:
                        return JsonResponse({'error': f'Invalid time format: {time_str}. Expected HH:MM or HH:MM:SS'}, status=400)
            elif isinstance(time_str, time):
                parsed_time = time_str
            else:
                return JsonResponse({'error': 'Time must be a string in HH:MM or HH:MM:SS format'}, status=400)
            
            # Validate date is not in the past
            if parsed_date < timezone.now().date():
                return JsonResponse({'error': 'Event date cannot be in the past'}, status=400)
            
            # Validate date and time combination for today
            if parsed_date == timezone.now().date() and parsed_time < timezone.now().time():
                return JsonResponse({'error': 'Event time cannot be in the past for today'}, status=400)
            
            # Validate category
            valid_categories = [choice[0] for choice in Event.EVENT_CATEGORIES]
            if data.get('category') not in valid_categories:
                return JsonResponse({
                    'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
                }, status=400)
            
            with transaction.atomic():
                event = Event(
                    superadmin=request.user,
                    name=data.get('name'),
                    category=data.get('category'),
                    sports_type=data.get('sports_type') or '',
                    country=data.get('country') or '',
                    team=data.get('team') or '',
                    stadium_name=data.get('stadium_name'),
                    stadium_image=data.get('stadium_image'),
                    event_logo=data.get('event_logo'),
                    date=parsed_date,
                    time=parsed_time,
                    normal_service_charge=data.get('normal_service_charge', 0),
                    reseller_service_charge=data.get('reseller_service_charge', 0),
                    total_tickets=data.get('total_tickets', 0),  
                    sold_tickets=data.get('sold_tickets', 0),   
                )
                
                # Validate the event before saving
                try:
                    event.full_clean()
                except ValidationError as e:
                    return JsonResponse({'error': f'Validation error: {str(e)}'}, status=400)
                
                event.save()
                
                sections_data = data.get('sections', [])
                if not isinstance(sections_data, list):
                    return JsonResponse({'error': 'Sections must be a list'}, status=400)
                
                for section_data in sections_data:
                    if not isinstance(section_data, dict):
                        return JsonResponse({'error': 'Each section must be an object with name and color'}, status=400)
                    
                    section_name = section_data.get('name')
                    section_color = section_data.get('color')
                    
                    if not section_name or not section_color:
                        return JsonResponse({'error': 'Each section must have name and color'}, status=400)
                    
                    # Validate color format
                    if not section_color.startswith('#') or len(section_color) not in [4, 7]:
                        return JsonResponse({'error': f'Invalid color format: {section_color}. Must be a hex color code'}, status=400)
                    
                    EventSection.objects.create(
                        event=event,
                        name=section_name,
                        color=section_color
                    )
                
                return JsonResponse({
                    'success': True,
                    'event_id': event.event_id,
                    'message': 'Event created successfully',
                    'total_tickets': event.total_tickets,
                    'sold_tickets': event.sold_tickets
                }, status=201)
                
        except ValidationError as e:
            return JsonResponse({'error': f'Validation error: {str(e)}'}, status=400)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return JsonResponse({
                'error': f'Error creating event: {str(e)}',
                'details': error_details if settings.DEBUG else None
            }, status=500)

class EventCreateView(SuperAdminMixin, CreateView):
    model = Event
    form_class = EventCreationForm
    template_name = 'events/event_create.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_colors'] = EventSection.COLORS
        return ctx

    def form_valid(self, form):
        try:
            with transaction.atomic():
                event = form.save(commit=False)
                event.superadmin = self.request.user
                event.save()
                
                sections = json.loads(self.request.POST.get('sections', '[]'))
                for section_data in sections:
                    section_form = SectionForm(section_data)
                    if section_form.is_valid():
                        EventSection.objects.create(
                            event=event,
                            name=section_form.cleaned_data['name'],
                            color=section_form.cleaned_data['color']
                        )
                    else:
                        raise ValueError("Invalid section data")
                
                self.send_creation_email(event)
                messages.success(self.request, 'Event created successfully')
                return redirect(reverse('events:superadmin_event_list'))

        except Exception as e:
            messages.error(self.request, f'Error creating event: {str(e)}')
            return self.form_invalid(form)

    def send_creation_email(self, event):
        subject = f'Event Created: {event.name}'
        message = f'''Event Details:
- ID: {event.event_id}
- Date: {event.date} {event.time}
- Stadium: {event.stadium_name}
- Sections: {event.sections.count()}

View event: {self.request.build_absolute_uri(
    reverse('events:superadmin_event_list')
)}'''
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.request.user.email],
                fail_silently=False
            )
        except Exception as e:
            messages.warning(self.request, f'Error sending confirmation email: {str(e)}')

class EventDeleteView(SuperAdminMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            event = get_object_or_404(Event, pk=self.kwargs['pk'])
            event_name = event.name
            event_id = event.event_id
            event.delete()
            
            self.send_deletion_email(event_name, event_id)
            messages.success(request, f'Event {event_name} ({event_id}) deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting event: {str(e)}')
        
        return redirect(reverse('events:superadmin_event_list'))

    def send_deletion_email(self, event_name, event_id):
        subject = f'Event Deleted: {event_name}'
        message = f'''Event deletion confirmed:
- ID: {event_id}
- Name: {event_name}
- Deletion Time: {timezone.now().strftime("%Y-%m-%d %H:%M")}

This action was performed by {self.request.user.email}'''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.request.user.email],
                fail_silently=False
            )
        except Exception as e:
            messages.error(f'Failed to send deletion email: {str(e)}')

class SuperadminEventListView(SuperAdminMixin, View):
    def get(self, request):
        events = Event.objects.filter(superadmin=request.user).order_by('-date', '-time')
        
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        paginator = Paginator(events, per_page)
        
        try:
            events_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            events_page = paginator.page(1)
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            events_data = []
            for event in events_page:
                events_data.append({
                    'event_id': event.event_id,
                    'name': event.name,
                    'category': event.category,
                    'stadium_name': event.stadium_name,
                    'date': event.date.isoformat(),
                    'time': event.time.strftime('%H:%M:%S'),
                    'min_price': float(event.sections.aggregate(Min('lower_price'))['lower_price__min'] or 0),
                    'max_price': float(event.sections.aggregate(Max('upper_price'))['upper_price__max'] or 0),
                    'total_tickets': event.total_tickets,
                    'sold_tickets': event.sold_tickets,
                    'total_sold_price': float(event.total_sold_price or 0),
                })
                
            return JsonResponse({
                'events': events_data,
                'page': page,
                'total_pages': paginator.num_pages,
                'total_events': paginator.count
            })
            
        return render(request, 'events/superadmin_event_list.html', {
            'events': events_page,
            'page_obj': events_page
        })

class ExpiredEventListView(SuperAdminMixin, ListView):
    template_name = 'events/expired_events.html'
    paginate_by = 10
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
            superadmin=self.request.user,
            date__lt=timezone.now().date()
        ).order_by('-date', '-time')


class EventUpdateAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, event_id):
        if not request.user.is_superadmin:
            return JsonResponse({'error': 'Only superadmins can update events'}, status=403)

        try:
            event = Event.objects.get(event_id=event_id, superadmin=request.user)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found or access denied'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        form_data = data.copy()
        sections_data = form_data.pop('sections', [])

        form = EventCreationForm(form_data, instance=event)
        if not form.is_valid():
            return JsonResponse({'error': form.errors}, status=400)

        try:
            with transaction.atomic():
                event = form.save()

                existing_sections = {str(s.id): s for s in event.sections.all()}

                for section_data in sections_data:
                    section_form = SectionForm(section_data)
                    if section_form.is_valid():
                        if 'id' in section_data and section_data['id'] in existing_sections:
                            section = existing_sections.pop(section_data['id'])
                            section.name = section_form.cleaned_data['name']
                            section.color = section_form.cleaned_data['color']
                            section.save()
                        else:
                            EventSection.objects.create(
                                event=event,
                                name=section_form.cleaned_data['name'],
                                color=section_form.cleaned_data['color']
                            )
                    else:
                        return JsonResponse({'error': section_form.errors}, status=400)

                for section in existing_sections.values():
                    section.delete()

                return JsonResponse({
                    'success': True,
                    'message': 'Event updated successfully',
                    'event_id': event.event_id
                })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class EventUpdateView(SuperAdminMixin, UpdateView):
    model = Event
    form_class = EventCreationForm
    template_name = 'events/event_update.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_colors'] = EventSection.COLORS
        return ctx
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                event = form.save()
                
                existing_sections = {str(s.id): s for s in event.sections.all()}
                sections = json.loads(self.request.POST.get('sections', '[]'))
                
                for section_data in sections:
                    section_form = SectionForm(section_data)
                    if section_form.is_valid():
                        if 'id' in section_data:
                            section_id = section_data['id']
                            if section_id in existing_sections:
                                section = existing_sections.pop(section_id)
                                section.name = section_form.cleaned_data['name']
                                section.color = section_form.cleaned_data['color']
                                section.save()
                            else:
                                EventSection.objects.create(
                                    event=event,
                                    **section_form.cleaned_data
                                )
                        else:
                            EventSection.objects.create(
                                event=event,
                                **section_form.cleaned_data
                            )
                
                for section in existing_sections.values():
                    section.delete()
                
                messages.success(self.request, 'Event updated successfully')
                return redirect(reverse('events:superadmin_event_list'))

        except Exception as e:
            messages.error(self.request, f'Error updating event: {str(e)}')
            return self.form_invalid(form)

class HomeView(ListView):
    template_name = 'events/home_new.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        from .models import EventCategory
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm()
        context['today'] = timezone.now().date()
        context['categories'] = EventCategory.objects.filter(is_active=True).order_by('order')
        context['upcoming_events'] = Event.objects.filter(
            date__gte=timezone.now().date()
        ).order_by('date', 'time')[:8]
        context['popular_events'] = Event.objects.annotate(
            total_sales=Sum('total_sold_price')
        ).order_by('-total_sales')[:8]
        return context

    def get_queryset(self):
        return Event.objects.none()

class EventSearchView(ListView):
    template_name = 'events/search_results.html'
    paginate_by = 10
    context_object_name = 'events'

    def get_queryset(self):
        query = self.request.GET.get('query')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        qs = Event.objects.all()
        
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(stadium_name__icontains=query) |
                Q(category__name__icontains=query)
            )
        
        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])
        
        return qs.annotate(
            min_price=Min('sections__lower_price'),
            max_price=Max('sections__upper_price')
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('query', '')
        return context

class AllEventsView(ListView):
    template_name = 'events/all_events.html'
    paginate_by = 10
    context_object_name = 'events'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'upcoming')
        team = self.request.GET.get('team')
        tournament = self.request.GET.get('tournament')
        
        qs = Event.objects.annotate(
            min_price=Min('sections__lower_price'),
            max_price=Max('sections__upper_price')
        )
        
        # Filter by team if provided
        if team:
            qs = qs.filter(team__iexact=team)
        
        # Filter by tournament/sports_type if provided
        if tournament:
            qs = qs.filter(sports_type__iexact=tournament)
        
        # Apply sorting
        if sort == 'upcoming':
            return qs.filter(date__gte=timezone.now().date()).order_by('date')
        elif sort == 'popular':
            return qs.order_by('-sold_tickets')
        elif sort == 'price_low':
            return qs.order_by('min_price')
        elif sort == 'price_high':
            return qs.order_by('-max_price')
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_team'] = self.request.GET.get('team', '')
        context['current_tournament'] = self.request.GET.get('tournament', '')
        context['current_sort'] = self.request.GET.get('sort', 'upcoming')
        return context

class CreateListingRedirectView(View):
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Redirecting to listing creation')
        return redirect('#') 

class TicketListView(View):
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Ticket list functionality coming soon')
        return render(request, 'events/ticket_list.html')


class SearchAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse([], safe=False)
        
        query = request.GET.get('query', '')[:100]
        print(query)
        events = Event.objects.filter(
            Q(name__icontains=query) |
            Q(stadium_name__icontains=query) |
            Q(category__icontains=query)
        ).annotate(
            min_price=Min('sections__lower_price'),
            max_price=Max('sections__upper_price')
        )[:10]
        
        data = [{
            'name': e.name,
            'category': e.get_category_display(),
            'date': e.date.strftime('%b %d, %Y'),
            'stadium': e.stadium_name,
            'min_price': str(e.min_price),
            'max_price': str(e.max_price),
            'url': reverse('events:event_tickets', args=[e.event_id])
        } for e in events]
        
        return JsonResponse(data, safe=False)

        
class NormalResellerPriceView(View):
    def get(self, request, *args, **kwargs):
        event_id = request.GET.get('event_id')
        try:
            event = Event.objects.get(event_id=event_id)
            return JsonResponse({
                'normal_price': str(event.normal_service_charge),
                'reseller_price': str(event.reseller_service_charge)
            })
        except EventSection.DoesNotExist:
            return JsonResponse({'error': 'Section not found'}, status=404)
        

class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = reverse_lazy('events:contact')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your message has been sent successfully!')
        self.send_notification_email(form.cleaned_data)
        return response
    
    def send_notification_email(self, data):
        subject = f"New Contact Message: {data['subject']}"
        message = f"""New message received:
        
From: {data['name']} <{data['email']}>
Phone: {data.get('phone', 'N/A')}
Subject: {data['subject']}
Message:
{data['message']}
"""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPERADMIN_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")


class PrivacyView(TemplateView):
    template_name = 'privacy_policy.html'


class AllEventsAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        sort = request.GET.get('sort', 'upcoming')
        category = request.GET.get('category', '')

        sports_type = request.GET.get('sports_type', '')
        country = request.GET.get('country', '')
        team = request.GET.get('team', '')

        qs = Event.objects.annotate(
            min_price=Min('sections__lower_price'),
            max_price=Max('sections__upper_price')
        )

        if category:
            qs = qs.filter(category=category)
        
        if sports_type:
            qs = qs.filter(sports_type__iexact=sports_type)
        
        if country:
            qs = qs.filter(country__iexact=country)
            
        if team:
            qs = qs.filter(team__iexact=team)

        if sort == 'upcoming':
            qs = qs.filter(date__gte=timezone.now().date()).order_by('date')
        elif sort == 'popular':
            qs = qs.order_by('-sold_tickets')
        elif sort == 'price_low':
            qs = qs.order_by('min_price')
        elif sort == 'price_high':
            qs = qs.order_by('-max_price')
        else:
            qs = qs.order_by('-date')

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(qs, per_page)

        try:
            events_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            events_page = paginator.page(1)

        events_data = []
        for event in events_page:
            events_data.append({
                'event_id': event.event_id,
                'name': event.name,
                'category': event.category,
                'sports_type': event.sports_type,
                'country': event.country,
                'team': event.team,
                'stadium_name': event.stadium_name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M:%S'),
                'min_price': float(event.min_price or 0),
                'max_price': float(event.max_price or 0),
                'total_tickets': event.total_tickets,
                'sold_tickets': event.sold_tickets,
                'time_left': event.time_left,
                'is_expired': event.is_expired
            })

        return JsonResponse({
            'events': events_data,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_events': paginator.count
        })


class EventSearchAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        query = request.GET.get('query', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        qs = Event.objects.all()

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(stadium_name__icontains=query) |
                Q(category__icontains=query) |
                Q(sports_type__icontains=query) |
                Q(country__icontains=query) |
                Q(team__icontains=query)
            )

        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])

        qs = qs.annotate(
            min_price=Min('sections__lower_price'),
            max_price=Max('sections__upper_price')
        ).order_by('-date')

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(qs, per_page)

        try:
            events_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            events_page = paginator.page(1)

        events_data = []
        for event in events_page:
            events_data.append({
                'event_id': event.event_id,
                'name': event.name,
                'category': event.category,
                'stadium_name': event.stadium_name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M:%S'),
                'min_price': float(event.min_price or 0),
                'max_price': float(event.max_price or 0),
                'total_tickets': event.total_tickets,
                'sold_tickets': event.sold_tickets,
                'time_left': event.time_left,
                'is_expired': event.is_expired
            })

        return JsonResponse({
            'events': events_data,
            'query': query,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_events': paginator.count
        })


class ExpiredEventsAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        if not request.user.is_superadmin:
            return JsonResponse({'error': 'Only superadmins can view expired events'}, status=403)

        qs = Event.objects.filter(
            superadmin=request.user,
            date__lt=timezone.now().date()
        ).order_by('-date', '-time')

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(qs, per_page)

        try:
            events_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            events_page = paginator.page(1)

        events_data = []
        for event in events_page:
            events_data.append({
                'event_id': event.event_id,
                'name': event.name,
                'category': event.category,
                'stadium_name': event.stadium_name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M:%S'),
                'total_tickets': event.total_tickets,
                'sold_tickets': event.sold_tickets,
                'total_sold_price': float(event.total_sold_price),
                'days_since_event': (timezone.now().date() - event.date).days
            })

        return JsonResponse({
            'events': events_data,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_events': paginator.count
        })


class EventDeleteAPIView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, event_id):
        if not request.user.is_superadmin:
            return JsonResponse({'error': 'Only superadmins can delete events'}, status=403)

        try:
            event = Event.objects.get(event_id=event_id, superadmin=request.user)
            event_name = event.name
            event_id = event.event_id
            event.delete()

            return JsonResponse({
                'success': True,
                'message': f'Event {event_name} ({event_id}) deleted successfully'
            })

        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found or access denied'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error deleting event: {str(e)}'}, status=500)

class EventSectionsAPIView(View):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, event_id):
        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        
        sections = event.sections.all().order_by('name')
        
        sections_data = []
        for section in sections:
            lower_price = section.lower_price if section.lower_price else 0
            upper_price = section.upper_price if section.upper_price else 0
            
            available_tickets = Ticket.objects.filter(
                event=event, 
                section=section, 
                sold=False
            ).aggregate(
                total_tickets=Sum('number_of_tickets')
            )['total_tickets'] or 0
            
            sections_data.append({
                'id': section.id,
                'name': section.name,
                'color': section.color,
                'lower_price': float(lower_price),
                'upper_price': float(upper_price),
                'available_tickets': available_tickets,
                'created_at': section.created.isoformat() if section.created else None
            })
        
        return JsonResponse({
            'event': {
                'event_id': event.event_id,
                'name': event.name,
                'category': event.category,
                'sports_type': event.sports_type,
                'country': event.country,
                'team': event.team,
                'stadium_name': event.stadium_name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M:%S'),
            },
            'sections': sections_data
        })


class CreateCategory(SuperAdminMixin , CreateView):
    def get(self , request):
        return render (request , 'events/create_category_inline.html')

class CategoryCreateAPIView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Try API authentication if not logged in via session
            user = authenticate_via_id_token(request)
            if user:
                request.user = user
            else:
                 return JsonResponse({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        if not request.user.is_superadmin:
             return JsonResponse({'error': 'Only superadmins can create categories'}, status=403)

        try:
            data = json.loads(request.body)
            name = data.get('name')
            raw_type = data.get('type') 
            country = data.get('country')

            if not name or not raw_type:
                 return JsonResponse({'error': 'Name and Type are required'}, status=400)
            
            # Normalize type: 'teams' -> 'team', 'tournaments' -> 'tournament'
            if raw_type.endswith('s'):
                normalized_type = raw_type[:-1] 
            else:
                normalized_type = raw_type
            
            # Basic validation
            if normalized_type not in dict(Category.TYPE_CHOICES):
                return JsonResponse({'error': 'Invalid category type'}, status=400)

            category, created = Category.objects.get_or_create(
                name=name,
                type=normalized_type,
                country=country
            )
            
            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name,
                'type': category.type,
                'country': category.country,
                'created': created,
                'message': 'Category created successfully' if created else 'Category already exists'
            })

        except Exception as e:
            print(f"Error creating category: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

class CategoryListAPIView(View):
    def get(self, request):
        
        categories = Category.objects.all().order_by('country', 'name')
        data = {
            'teams': {},
            'tournaments': {}
        }

        for cat in categories:
            # Map database type to frontend keys
            if cat.type == 'team':
                if cat.country not in data['teams']:
                    data['teams'][cat.country] = []
                data['teams'][cat.country].append({
                    'id': cat.id,
                    'name': cat.name
                })
            elif cat.type == 'tournament':
                if cat.country not in data['tournaments']:
                    data['tournaments'][cat.country] = []
                data['tournaments'][cat.country].append({
                    'id': cat.id,
                    'name': cat.name
                })
        
        return JsonResponse(data)

class CategoryDeleteAPIView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            user = authenticate_via_id_token(request)
            if user:
                request.user = user
            else:
                 return JsonResponse({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, category_id):
        if not request.user.is_superadmin:
             return JsonResponse({'error': 'Only superadmins can delete categories'}, status=403)

        try:
            category = Category.objects.get(id=category_id)
            category_name = category.name
            category_type = category.type
            category.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{category_type.capitalize()} "{category_name}" deleted successfully'
            })
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class CategoryUpdateAPIView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            user = authenticate_via_id_token(request)
            if user:
                request.user = user
            else:
                 return JsonResponse({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def put(self, request, category_id):
        if not request.user.is_superadmin:
             return JsonResponse({'error': 'Only superadmins can update categories'}, status=403)

        try:
            category = Category.objects.get(id=category_id)
            data = json.loads(request.body)
            
            # Update fields if provided
            if 'name' in data:
                category.name = data['name']
            if 'country' in data:
                category.country = data['country']
            if 'type' in data:
                raw_type = data['type']
                if raw_type.endswith('s'):
                    normalized_type = raw_type[:-1]
                else:
                    normalized_type = raw_type
                
                if normalized_type in dict(Category.TYPE_CHOICES):
                    category.type = normalized_type
            
            category.save()
            
            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name,
                'type': category.type,
                'country': category.country,
                'message': 'Category updated successfully'
            })
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)