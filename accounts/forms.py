from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
from phonenumber_field.formfields import PhoneNumberField
from django_countries import countries

class UserSignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
            'data-validation': 'password'
        })
    )
    password2 = forms.CharField(
        label=_("Re-enter Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password',
            'data-validation': 'password-match'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'user-type-radio',
            'data-behavior': 'user-type-toggle'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_type']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John',
                'pattern': '[A-Za-z ]+',
                'data-validation': 'name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe',
                'pattern': '[A-Za-z ]+',
                'data-validation': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'data-validation': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'data-validation': 'phone'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'] = PhoneNumberField(
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'data-validation': 'phone'
            }),
            region='US'
        )

        self.fields['country'] = forms.ChoiceField(
            choices=[],
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control conditional-field',
                'data-conditional': 'user-type-Reseller',
            })
        )
        self.fields['country'].choices=countries
        self.fields['city'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control conditional-field',
                'placeholder': 'New York',
                'data-conditional': 'user-type-Reseller',
            })
        )
        self.fields['street_no'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control conditional-field',
                'placeholder': '123 Main St',
                'data-conditional': 'user-type-Reseller',
            })
        )
        self.fields['social_media_link'] = forms.URLField(
            required=False,
            widget=forms.URLInput(attrs={
                'class': 'form-control conditional-field',
                'placeholder': 'https://facebook.com/yourpage',
                'data-conditional': 'user-type-Reseller',
            })
        )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        user_type = cleaned_data.get('user_type')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', ValidationError(_("Passwords do not match")))


        if user_type == 'Reseller':
            required_fields = ['country', 'city', 'street_no']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, ValidationError(
                        _("This field is required for Reseller accounts")))

        return cleaned_data

class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'autocomplete': 'email'
        })
    )

class SuperAdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'superadmin@example.com',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Superadmin password',
            'autocomplete': 'current-password'
        })
    )

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )

    error_messages = {
        'invalid_login': _("Invalid email or password"),
        'inactive': _("This account is inactive"),
        'unverified': _("Email not verified"),
    }

class ForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'autocomplete': 'email'
        })
    )

class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'country', 'city', 'street_no', 'social_media_link']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'street_no': forms.TextInput(attrs={'class': 'form-control'}),
            'social_media_link': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type == 'Normal':
            del self.fields['country']
            del self.fields['city']
            del self.fields['street_no']
            del self.fields['social_media_link']
        self.fields['country'] = forms.ChoiceField(
            choices=[],
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control',
            })
        )
        self.fields['country'].choices=countries


class UpdatePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password',
            'autocomplete': 'current-password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )

class UserUpdateBySuperAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'is_verified': forms.RadioSelect(choices=((True, 'Yes'), (False, 'No'))),
            'verified_seller': forms.RadioSelect(choices=((True, 'Yes'), (False, 'No'))),
            'is_superadmin': forms.RadioSelect(choices=((True, 'Yes'), (False, 'No'))),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['is_verified', 'verified_seller', 'is_superadmin']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

