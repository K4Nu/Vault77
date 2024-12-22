from allauth.account.forms import SignupForm
from django import forms
from .models import Profile, CustomUser


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
        user = super(MyCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # Handle profile creation differently for superusers and staff
        if not (user.is_superuser or user.is_staff):
            Profile.objects.create(
                user=user,
                first_name=self.cleaned_data.get('first_name'),
                last_name=self.cleaned_data.get('last_name'),
                phone_number=self.cleaned_data.get('phone_number', None),
                newsletter=self.cleaned_data.get('newsletter', False),
            )

        # Save additional user fields
        user.first_name = self.cleaned_data.get('first_name', "")
        user.last_name = self.cleaned_data.get('last_name', "")
        user.save()

        return user

