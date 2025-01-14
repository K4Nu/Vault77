from allauth.account.forms import SignupForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib.auth import get_user, password_validation
from django.core.exceptions import ValidationError
from .models import Profile, CustomUser
from allauth.account.utils import get_adapter, send_email_confirmation
import os

class MyCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=50, label='First Name', required=True)
    last_name = forms.CharField(max_length=50, label='Last Name', required=True)
    phone_number = forms.CharField(max_length=20, label='Phone Number', required=False)
    newsletter = forms.BooleanField(label='Subscribe to Newsletter', required=False)

    field_order = ['email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2','newsletter']

    def clean_email(self):
        email=self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email

    def save(self, request):
        # Save the user instance created by the parent class
        user=super(MyCustomSignupForm,self).save(request)
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.save()

        if not(user.is_superuser or user.is_staff):
            profile=user.profile
            profile.phone_number=self.cleaned_data.get('phone_number')
            profile.newsletter=self.cleaned_data.get('newsletter',False)
            profile.save()

        return user
class MyCustomResetPasswordForm(ResetPasswordForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)
        self.users = CustomUser.objects.filter(email=email)
        if not self.users.exists():
            raise forms.ValidationError("Email does not exist")
        elif SocialAccount.objects.filter(user__email=email).exists():
            raise forms.ValidationError("Email is associated with a social account")
        return email


class CustomChangePasswordForm(ChangePasswordForm):
    def clean(self):
        cleaned_data=super().clean()
        if SocialAccount.objects.filter(user=self.user).exists():
            raise ValidationError("You cannot reset your password using a social account")
        return cleaned_data


class CustomChangeEmailForm(forms.Form):
    email1 = forms.EmailField(label='New Email')
    email2 = forms.EmailField(label='Confirm New Email')

    def clean(self):
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email1")
        email2 = cleaned_data.get("email2")

        if email1 and email2:
            # Clean emails using adapter
            email1 = get_adapter().clean_email(email1)
            email2 = get_adapter().clean_email(email2)

            # Check if emails match
            if email1 != email2:
                raise forms.ValidationError("Emails do not match")

            # Comprehensive email uniqueness check
            if (CustomUser.objects.filter(email=email1).exists() or
                    EmailAddress.objects.filter(email=email1).exists() or
                    SocialAccount.objects.filter(user__email=email1).exists()):
                raise forms.ValidationError("Email already in use")

            cleaned_data['email1'] = email1
            cleaned_data['email2'] = email2

        return cleaned_data

class ResendEmailForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-gray-700',
            'placeholder': 'Enter your email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)

        # Check if email exists in the system
        if not EmailAddress.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address")

        # Check if email is already verified
        if EmailAddress.objects.filter(email=email, verified=True).exists():
            raise forms.ValidationError("This email is already verified")

        # Check if associated with social account
        if SocialAccount.objects.filter(user__email=email).exists():
            raise forms.ValidationError("This email is associated with a social account. Please login using your social account.")

        return email

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone_number = forms.CharField(max_length=15, required=False)
    image = forms.ImageField(required=False)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Print for debugging
            extension = os.path.splitext(image.name)[1].lower()  # includes the dot
            print(f"File extension: {extension}")
            print(f"Allowed types: {settings.ALLOWED_IMAGE_FILETYPES}")

            # Remove dot from extension for comparison since your settings don't include dots
            extension = extension.lstrip('.')  # Remove dot if present
            if extension not in settings.ALLOWED_IMAGE_FILETYPES:
                raise forms.ValidationError(
                    f"Image file type {extension} is not allowed. Allowed types are: {settings.ALLOWED_IMAGE_FILETYPES}")
            if image.size > settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError("Image file size is too large.")
        return image