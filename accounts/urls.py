from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign_up'),
    path('sign-in/', views.UserLoginView.as_view(), name='sign_in'),
    path('sign-out/', views.sign_out, name='sign_out'),
    
    path('superadmin/secured/sign-in/', views.SuperadminLoginView.as_view(), name='superadmin_login'),
    
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uuid:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/update-profile/', views.update_profile, name='update_profile'),
    path('profile/update-password/', views.update_password, name='update_password'),
    
    path('superadmin/accounts/', views.SuperadminUserListView.as_view(), name='superadmin_accounts'),
    path('superadmin/accounts/update/<uuid:user_id>/', 
         views.SuperadminUserUpdateView.as_view(), name='superadmin_update_user'),
    path('superadmin/accounts/delete/<uuid:user_id>/', 
         views.SuperadminUserDeleteView.as_view(), name='superadmin_delete_user'),
]