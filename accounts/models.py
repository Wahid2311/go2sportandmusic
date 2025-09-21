import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superadmin', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('user_type', 'Reseller')
        extra_fields.setdefault('verified_seller', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superadmin') is not True:
            raise ValueError('Superuser must have is_superadmin=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('Normal', 'Normal'),
        ('Reseller', 'Reseller'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[a-zA-Z ]*$', 'Only letters and spaces are allowed')
    ])
    last_name = models.CharField(max_length=50, validators=[
        RegexValidator(r'^[a-zA-Z ]*$', 'Only letters and spaces are allowed')
    ])
    phone = PhoneNumberField(region='US', unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    street_no = models.CharField(max_length=100, null=True, blank=True)
    social_media_link = models.URLField(max_length=200, null=True, blank=True)
    verified_seller = models.BooleanField(default=False)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['email', 'is_verified', 'is_superadmin']),
        ]

    def __str__(self):
        return self.email

class EmailVerificationToken(models.Model):
    TOKEN_TYPE_CHOICES = (
        ('signup', 'Signup Verification'),
        ('password_reset', 'Password Reset'),
        ('superadmin', 'Superadmin Login'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()
