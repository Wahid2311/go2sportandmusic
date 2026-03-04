import datetime
import hmac
from hashlib import sha256
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import User, EmailVerificationToken
import requests
from .forms import (
    UserSignUpForm, EmailVerificationForm, SuperAdminLoginForm,
    UserLoginForm, ForgotPasswordForm, ResetPasswordForm,
    UserProfileForm, UpdatePasswordForm,
    UserUpdateBySuperAdminForm
)

class BaseViewMixin:
    def handle_error(self, request, message, redirect_url):
        messages.error(request, message)
        return redirect(redirect_url)

    def send_verification_email(self,  request,user, token_type):
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + datetime.timedelta(days=1),
            token_type=token_type
        )
        subject = 'Email Verification Required'
        verification_url = request.build_absolute_uri(
            reverse('accounts:verify_email', args=[token.token])
        )
        message = f'''Click the link to verify your email:
{verification_url}
This link expires in 24 hours.'''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.set_password(form.cleaned_data['password1'])
                user.save()

                if user.user_type == 'Reseller':
                    user.country = form.cleaned_data['country']
                    user.city = form.cleaned_data['city']
                    user.street_no = form.cleaned_data['street_no']
                    user.social_media_link = form.cleaned_data['social_media_link']
                    user.save()

            BaseViewMixin().send_verification_email(request,user, 'signup')
            messages.success(request, 'Verification email sent! Check your inbox.')
            return redirect('accounts:sign_in')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserSignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})

class UserLoginView(View, BaseViewMixin):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/signin.html', {'form': UserLoginForm()})

    def post(self, request):
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if user.is_superadmin:
                return self.handle_error(request,
                    'Superadmin should use dedicated sign in url.',
                    'accounts:sign_in'
                )
            
            if not user.is_verified:
                self.send_verification_email(request, user, 'signup')
                return self.handle_error(request,
                    'Email not verified. New verification link sent.',
                    'accounts:sign_in'
                )
            
            if user.user_type == 'Reseller' and not user.verified_seller:
                return self.handle_error(request,
                    'Account pending admin approval.',
                    'accounts:sign_in'
                )
            
            login(request, user)
            return redirect('accounts:dashboard')
        
        return render(request, 'accounts/signin.html', {'form': form})

class SuperadminLoginView(View, BaseViewMixin):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superadmin:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/superadmin_login.html', {'form': SuperAdminLoginForm()})
    
    def post(self, request):
        form = SuperAdminLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email, is_superadmin=True)
                if not user.check_password(password):
                    raise User.DoesNotExist
                
                self.send_verification_email(request, user, 'superadmin')
                messages.success(request, 'Superadmin verification email sent')
                return redirect('accounts:superadmin_login')
            
            except User.DoesNotExist:
                messages.error(request, 'Invalid superadmin credentials')
        
        return render(request, 'accounts/superadmin_login.html', {'form': form})

def verify_email(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token)
        if verification.is_used or verification.expires_at < timezone.now():
            raise EmailVerificationToken.DoesNotExist
        
        verification.is_used = True
        verification.save()
        
        user = verification.user
        if verification.token_type == 'superadmin':
            user.is_verified = True
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Superadmin verification successful!')
            return redirect('accounts:dashboard')
        
        elif verification.token_type == 'signup':
            user.is_verified = True
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified successfully! Please login.')
            return redirect('accounts:sign_in')
        
        else:
            raise EmailVerificationToken.DoesNotExist
    
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link')
        return redirect('accounts:resend_verification')

def resend_verification(request):
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_verified:
                    messages.info(request, 'Email is already verified')
                    return redirect('accounts:sign_in')
                
                BaseViewMixin().send_verification_email(user, 'signup')
                messages.success(request, 'New verification link sent')
                return redirect('accounts:sign_in')
            
            except User.DoesNotExist:
                messages.error(request, 'Email not registered')
    
    else:
        form = EmailVerificationForm()
    
    return render(request, 'accounts/resend_verification.html', {'form': form})

class ForgotPasswordView(View, BaseViewMixin):
    def get(self, request):
        return render(request, 'accounts/forgot_password.html', {'form': ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = EmailVerificationToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + datetime.timedelta(days=1),
                    token_type='password_reset'
                )
                subject = 'Password Reset Request'
                reset_url = request.build_absolute_uri(
                    reverse('accounts:reset_password', args=[token.token])
                )
                message = f'''Click the link to reset your password:
{reset_url}
This link expires in 24 hours.'''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link sent to your email')
                return redirect('accounts:sign_in')
            except User.DoesNotExist:
                messages.error(request, 'Email not registered')
        
        return render(request, 'accounts/forgot_password.html', {'form': form})

class ResetPasswordView(View, BaseViewMixin):
    def get(self, request, token):
        try:
            verification = EmailVerificationToken.objects.get(
                token=token,
                token_type='password_reset',
                is_used=False
            )
            if verification.expires_at < timezone.now():
                raise EmailVerificationToken.DoesNotExist
            
            verification.is_used = True
            verification.save()
            
            return render(request, 'accounts/reset_password.html', {
                'form': ResetPasswordForm(user=verification.user),
                'token': token
            })
        
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, 'Invalid or expired password reset link')
            return redirect('accounts:sign_in')

    def post(self, request, token):
        try:
            verification = EmailVerificationToken.objects.get(
                token=token,
                token_type='password_reset',
                is_used=False
            )
            if verification.expires_at < timezone.now():
                raise EmailVerificationToken.DoesNotExist
                
            form = ResetPasswordForm(user=verification.user, data=request.POST)
            if form.is_valid():
                user = verification.user
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                verification.is_used = True
                verification.save()
                messages.success(request, 'Password reset successfully! Please login.')
                return redirect('accounts:sign_in')
            
            return render(request, 'accounts/reset_password.html', {
                'form': form,
                'token': token
            })
            
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, 'Invalid or expired password reset link')
            return redirect('accounts:sign_in')

@login_required
def dashboard(request):
    return redirect('accounts:profile')

@login_required
def profile(request):
    user = request.user
    
    if request.user.is_superadmin:
        base = 'accounts/superadmin_dashboard.html'
    elif request.user.user_type == 'Reseller':
        base = 'accounts/reseller_dashboard.html'
    else:
        base= 'accounts/normal_dashboard.html'
    return render(request, 'accounts/profile.html', {
        'user': user,
        'base_template': base,
    })


@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Error updating profile')
    else:
        form = UserProfileForm(instance=user)

    if request.user.is_superadmin:
        base = 'accounts/superadmin_dashboard.html'
    elif request.user.user_type == 'Reseller':
        base = 'accounts/reseller_dashboard.html'
    else:
        base= 'accounts/normal_dashboard.html'
    
    return render(request, 'accounts/update_profile.html', {'form': form,'base_template':base})

@login_required
def update_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['current_password']):
                messages.error(request, 'Current password is incorrect')
            else:
                request.user.set_password(form.cleaned_data['new_password1'])
                request.user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('accounts:profile')
    else:
        form = UpdatePasswordForm()
    if request.user.is_superadmin:
        base = 'accounts/superadmin_dashboard.html'
    elif request.user.user_type == 'Reseller':
        base = 'accounts/reseller_dashboard.html'
    else:
        base= 'accounts/normal_dashboard.html'
    
    return render(request, 'accounts/update_password.html', {'form': form,'base_template':base})

def sign_out(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('accounts:sign_in')

class SuperadminUserListView(ListView, BaseViewMixin):
    model = User
    template_name = 'accounts/superadmin_accounts.html'
    context_object_name = 'users'
    paginate_by = 10 

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date_joined')
        
        filter_param = self.request.GET.get('filter')
        if filter_param == 'unverified_resellers':
            queryset = queryset.filter(
                user_type='Reseller',
                verified_seller=False
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['current_filter'] = self.request.GET.get('filter', '')
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        context['users'] = users
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin:
            return self.handle_error(request,
                'Unauthorized access',
                'accounts:sign_in'
            )
        return super().dispatch(request, *args, **kwargs)

class SuperadminUserUpdateView(UpdateView, BaseViewMixin):
    model = User
    form_class = UserUpdateBySuperAdminForm
    template_name = 'accounts/superadmin_update_user.html'
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin:
            return self.handle_error(request,
                'Unauthorized access',
                'accounts:sign_in'
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'User updated successfully')
        return reverse('accounts:superadmin_accounts')

class SuperadminUserDeleteView(View, BaseViewMixin):
    def post(self, request, user_id):
        if not request.user.is_authenticated or not request.user.is_superadmin:
            return self.handle_error(request,
                'Unauthorized access',
                'accounts:sign_in'
            )
        
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            return self.handle_error(request,
                'Cannot delete your own account',
                'accounts:superadmin_accounts'
            )
        
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('accounts:superadmin_accounts')

