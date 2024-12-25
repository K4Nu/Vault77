from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.shortcuts import redirect
from django.contrib import messages
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from .models import CustomUser, Profile
from django.http import HttpResponseRedirect
from allauth.core.exceptions import ImmediateHttpResponse
from django.urls import reverse

@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    if not request:
        return

    user = sociallogin.user
    email = user.email

    # Check if a user already exists with this email
    existing_user = CustomUser.objects.filter(email=email).first()

    if existing_user:
        # Check if the existing user has a linked social account
        if SocialAccount.objects.filter(user=existing_user).exists():
            # Allow login if the user is already a social account user
            sociallogin.connect(request, existing_user)
        else:
            # Block login if the user is a regular email/password user
            messages.error(request, "An account with this email already exists. Please log in using your email and password.")
            # Raise ImmediateHttpResponse to stop the authentication flow
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_login')))

    # Save the user if not already saved
    if not user.pk:
        user.save()

    # Create profile if it doesn't exist
    if not Profile.objects.filter(user=user).exists():
        Profile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    if not EmailAddress.objects.filter(user=user).exists():
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True,
        )