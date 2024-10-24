from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from docutils.nodes import label

# Get the custom user model (AppUser in this case)
User = get_user_model()

class CustomSignupForm(SignupForm):
    firstname = forms.CharField(max_length=100, label="First Name",widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    lastname = forms.CharField(max_length=100, label="Last Name",widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    newsletter = forms.BooleanField(
        label="Do you want to join our newsletter and get first updates about new products?",
        required=False
    )
    # overwrite of init for field order
    def __init__(self,*args,**kwargs):
        super(CustomSignupForm, self).__init__(*args,**kwargs)
        field_order = [
            'email',
            'firstname',
            'lastname',
            'password1',
            'password2',
            'newsletter',
        ]

        # Reorder the fields using the specified order
        self.order_fields(field_order)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if the email already exists in a case-insensitive way
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user is already registered with this email address.")
        return email

    def save(self, request):
        # Save the user using the parent class's save method
        user = super(CustomSignupForm, self).save(request)
        user.firstname = self.cleaned_data['firstname']
        user.lastname = self.cleaned_data['lastname']
        user.newsletter=self.cleaned_data.get("newsletter", False)
        user.save()
        return user

class UserInfoForm(forms.Form):
    firstname = forms.CharField(
        max_length=100,
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    lastname = forms.CharField(
        max_length=100,
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})  # Corrected placeholder
    )

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(), label="Current Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not check_password(current_password, self.user.password):
            raise forms.ValidationError("Your current password is incorrect.")
        return current_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise forms.ValidationError("The new password must be at least 8 characters long.")
        if not any(char.isdigit() for char in new_password1):
            raise forms.ValidationError("The new password must contain at least one digit.")
        if not any(char.isalpha() for char in new_password1):
            raise forms.ValidationError("The new password must contain at least one letter.")
        return new_password1

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        return cleaned_data


from django.contrib.auth import get_user_model


class EmailChangeForm(forms.Form):
    email1 = forms.EmailField(max_length=255, label="New Email")
    email2 = forms.EmailField(max_length=255, label="Confirm New Email")

    def clean(self):
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email1")
        email2 = cleaned_data.get("email2")

        # Check if emails match
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError("The emails do not match.")

        return cleaned_data

    def clean_email1(self):
        email1 = self.cleaned_data.get("email1")

        # Check if email already exists in the database
        User = get_user_model()
        if User.objects.filter(email=email1).exists():
            raise forms.ValidationError("This email is already in use.")

        return email1
