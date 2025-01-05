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
from django.db.models.signals import post_save, pre_save
from allauth.account.forms import SetPasswordForm

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

@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance,
                               first_name=instance.first_name,
                               last_name=instance.last_name)

@receiver(social_account_added)
def social_account_added_handler(sender,request,sociallogin,**kwargs):
    user=sociallogin.user
    email=user.email

    if not Profile.objects.filter(user=user).exists():
        Profile.objects.create(user=user,
                                   first_name=user.first_name,
                                   last_name=user.last_name)

    if not EmailAddress.objects.filter(email=email).exists():
        EmailAddress.objects.create(user=user,email=email,primary=True,verified=False)
    return

