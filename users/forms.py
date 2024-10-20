from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model

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