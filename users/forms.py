from allauth.account.forms import SignupForm, ResetPasswordForm, ChangePasswordForm
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib.auth import get_user, password_validation
from django.core.exceptions import ValidationError
from .models import Profile, CustomUser
from allauth.account.utils import get_adapter


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
