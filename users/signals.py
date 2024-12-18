from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from .models import CustomUser,Profile
from django.core.exceptions import ValidationError
from allauth.account.models import EmailAddress
from django.db.models.signals import post_save


@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    email = sociallogin.user.email
    try:
        existing_user = CustomUser.objects.get(email=email)
        sociallogin.connect(request, existing_user)
        if not EmailAddress.objects.filter(user=existing_user, email=email).exists():
            EmailAddress.objects.create(user=existing_user, email=email, primary=True, verified=True)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(email=email, password=None)
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        Profile.objects.get_or_create(user=user,first_name=sociallogin.user.first_name, last_name=sociallogin.user.last_name)  # Ensure profile is created


