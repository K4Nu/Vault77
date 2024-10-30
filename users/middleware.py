from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

User = get_user_model()

class GoogleLoginRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a Google login attempt
        if request.path == reverse('google_login'):  # Use 'google_login' or appropriate name
            # Get the email from the social login data if available
            email = request.GET.get('email')

            # If email exists, check the database for a User without a SocialAccount
            if email and User.objects.filter(email=email).exists() and not SocialAccount.objects.filter(user__email=email).exists():
                # Redirect back to login with an error message
                messages.error(request, "An account with this email already exists. Please log in with your credentials.")
                return redirect(reverse('account_login'))

        # Continue processing the request
        response = self.get_response(request)
        return response
