from allauth.socialaccount.signals import pre_social_login, social_account_added
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
def pre_social_login_handler(sender,request,sociallogin,**kwargs):
    if not request:
        return

    email=sociallogin.user.email
    existing_user=CustomUser.objects.filter(email=email).first()

    if existing_user and not SocialAccount.objects.filter(user=existing_user).exists():
        messages.error(request, "Account exists with this email. Please login with email/password.")
        raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_login')))

    return

@receiver(social_account_added)
def social_account_added_handler(sender,request,sociallogin,**kwargs):
    if not sociallogin.is_existing:
        user=sociallogin.user
        email=user.email

        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user,
                                   first_name=user.first_name,
                                   last_name=user.last_name)

        if not EmailAddress.objects.filter(email=email).exists():
            EmailAddress.objects.create(user=user,email=email,primary=True,verified=False)
    return